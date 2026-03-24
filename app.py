from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

COMPLEXITY_LABELS = {
    1: "Simple table data (one product per row)",
    2: "Basic structured text & lists",
    3: "Simple mixed content (text + tables)",
    4: "Standard business documents",
    5: "Multi-section reports",
    6: "Complex tables with nested data",
    7: "Mixed media with charts & graphs",
    8: "Dense technical documents",
    9: "Complex multi-layout pages",
    10: "Highly complex (nested tables, images, mixed layouts)",
}

# ~$0.01 per page base rate; complexity multiplier (1x–3x) drives the range
BASE_COST_PER_PAGE_LOW = 0.01
BASE_COST_PER_PAGE_HIGH = 0.01

# Complexity 1 = 1.0x, Complexity 10 = 3.0x (linear)
COMPLEXITY_MULTIPLIER_MIN = 1.0
COMPLEXITY_MULTIPLIER_MAX = 3.0


def get_complexity_multiplier(complexity: int) -> float:
    return COMPLEXITY_MULTIPLIER_MIN + (complexity - 1) * (
        (COMPLEXITY_MULTIPLIER_MAX - COMPLEXITY_MULTIPLIER_MIN) / 9
    )


@app.route("/")
def index():
    return render_template("index.html", complexity_labels=COMPLEXITY_LABELS)


@app.route("/pricing-models")
def pricing_models():
    return render_template("pricing_models.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    complexity = max(1, min(10, int(data.get("complexity", 1))))
    num_pdfs = max(1, min(1000, int(data.get("num_pdfs", 1))))
    pages = max(1, min(1000, int(data.get("pages", 5))))

    multiplier = get_complexity_multiplier(complexity)

    cost_per_pdf_low = pages * BASE_COST_PER_PAGE_LOW * multiplier
    cost_per_pdf_high = pages * BASE_COST_PER_PAGE_HIGH * multiplier

    monthly_low = cost_per_pdf_low * num_pdfs
    monthly_high = cost_per_pdf_high * num_pdfs

    yearly_low = monthly_low * 12
    yearly_high = monthly_high * 12

    return jsonify({
        "complexity_label": COMPLEXITY_LABELS[complexity],
        "complexity_multiplier": round(multiplier, 2),
        "cost_per_page_low": round(BASE_COST_PER_PAGE_LOW * multiplier, 4),
        "cost_per_page_high": round(BASE_COST_PER_PAGE_HIGH * multiplier, 4),
        "cost_per_pdf_low": round(cost_per_pdf_low, 2),
        "cost_per_pdf_high": round(cost_per_pdf_high, 2),
        "monthly_low": round(monthly_low, 2),
        "monthly_high": round(monthly_high, 2),
        "yearly_low": round(yearly_low, 2),
        "yearly_high": round(yearly_high, 2),
        "total_pages_per_month": pages * num_pdfs,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
