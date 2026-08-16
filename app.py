from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import re


# ============================================================
# APP
# ============================================================

app = Flask(__name__)
CORS(app)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
KB_FILE = os.path.join(BASE_DIR, "knowledge_base.json")


# ============================================================
# KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():

    if not os.path.exists(KB_FILE):
        return []

    try:

        with open(
            KB_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):

            for key in [
                "documents",
                "knowledge",
                "entries",
                "data",
                "items"
            ]:

                if key in data and isinstance(data[key], list):
                    return data[key]

            return [data]

    except Exception as error:

        print("Knowledge base error:", error)

        return []


KNOWLEDGE_BASE = load_knowledge_base()


# ============================================================
# TEXT HELPERS
# ============================================================

def extract_text(item):

    if isinstance(item, str):
        return item

    if isinstance(item, dict):

        parts = []

        for key in [
            "title",
            "content",
            "text",
            "description",
            "summary",
            "answer"
        ]:

            value = item.get(key)

            if value:
                parts.append(str(value))

        return " ".join(parts)

    return str(item)


def retrieve(decision, limit=5):

    decision_words = set(
        re.findall(
            r"[a-zA-Z]{3,}",
            decision.lower()
        )
    )

    scored = []

    for item in KNOWLEDGE_BASE:

        text = extract_text(item)

        words = set(
            re.findall(
                r"[a-zA-Z]{3,}",
                text.lower()
            )
        )

        score = len(
            decision_words.intersection(words)
        )

        if score > 0:
            scored.append(
                (score, item)
            )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    results = []

    for score, item in scored[:limit]:

        if isinstance(item, dict):

            results.append({
                "title":
                    item.get(
                        "title",
                        "Retrieved intelligence"
                    ),

                "content":
                    item.get(
                        "content",
                        item.get(
                            "text",
                            item.get(
                                "description",
                                ""
                            )
                        )
                    )
            })

        else:

            results.append({
                "title":
                    "Knowledge Base",

                "content":
                    str(item)
            })

    return results


# ============================================================
# SIMPLE AI DECISION ENGINE
# ============================================================

def analyze_decision(decision):

    retrieved = retrieve(decision)

    lower = decision.lower()

    factors = [
        "Alignment with the primary objective",
        "Long-term value and expected impact",
        "Cost, time and resource requirements"
    ]

    risks = [
        "Uncertainty in future outcomes",
        "Opportunity cost of the selected option",
        "Execution or implementation risk"
    ]

    opportunities = [
        "Potential for long-term growth",
        "Ability to create additional options later",
        "Potential strategic or practical advantages"
    ]

    tradeoffs = [
        "Short-term benefit versus long-term value",
        "Risk versus potential return",
        "Flexibility versus commitment"
    ]


    if any(
        word in lower
        for word in [
            "career",
            "job",
            "phd",
            "study",
            "degree"
        ]
    ):

        factors = [
            "Career trajectory",
            "Skill development",
            "Research and industry exposure"
        ]

        risks = [
            "Time investment",
            "Changing industry requirements",
            "Opportunity cost"
        ]

        opportunities = [
            "Specialized expertise",
            "Higher-value career options",
            "Research and innovation opportunities"
        ]

        tradeoffs = [
            "Immediate income versus long-term specialization",
            "Industry experience versus academic depth",
            "Flexibility versus specialization"
        ]


    if any(
        word in lower
        for word in [
            "business",
            "company",
            "startup",
            "investment"
        ]
    ):

        factors = [
            "Expected return",
            "Market opportunity",
            "Capital and execution requirements"
        ]

        risks = [
            "Market uncertainty",
            "Financial exposure",
            "Execution risk"
        ]

        opportunities = [
            "Market growth",
            "Scalability",
            "Competitive advantage"
        ]

        tradeoffs = [
            "Risk versus return",
            "Growth versus stability",
            "Capital investment versus flexibility"
        ]


    if retrieved:

        summary = (
            "DecisionLens retrieved relevant information "
            "from its knowledge base and combined it with "
            "structured decision factors. The strongest "
            "choice should be evaluated against your goals, "
            "constraints, risk tolerance and long-term impact."
        )

    else:

        summary = (
            "DecisionLens evaluated the decision using a "
            "structured reasoning framework covering goals, "
            "risks, opportunities and trade-offs."
        )


    recommendation = (
        "Prioritize the option with the strongest "
        "long-term alignment while keeping downside risk manageable."
    )


    return {
        "decision": decision,

        "recommendation":
            recommendation,

        "summary":
            summary,

        "confidence":
            82 if retrieved else 74,

        "factors":
            factors,

        "risks":
            risks,

        "opportunities":
            opportunities,

        "tradeoffs":
            tradeoffs,

        "evidence":
            retrieved
    }


# ============================================================
# FRONTEND ROUTES
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/dashboard.html")
def dashboard():

    return send_from_directory(
        FRONTEND_DIR,
        "dashboard.html"
    )


@app.route("/result.html")
def result():

    return send_from_directory(
        FRONTEND_DIR,
        "result.html"
    )


@app.route("/<path:filename>")
def frontend_files(filename):

    return send_from_directory(
        FRONTEND_DIR,
        filename
    )


# ============================================================
# API
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({
        "status": "online",
        "service": "DecisionLens AI",
        "knowledge_base":
            len(KNOWLEDGE_BASE)
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        decision = str(
            data.get("decision", "")
        ).strip()

        if not decision:

            return jsonify({
                "error":
                    "Decision text is required."
            }), 400


        result = analyze_decision(
            decision
        )

        return jsonify(result)


    except Exception as error:

        print(
            "ANALYSIS ERROR:",
            repr(error)
        )

        return jsonify({
            "error":
                "The decision engine encountered an error."
        }), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
