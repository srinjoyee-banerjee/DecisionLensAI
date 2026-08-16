import os
import json
import re

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from google import genai


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
KB_PATH = os.path.join(BASE_DIR, "knowledge_base.json")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

CORS(app)


# ============================================================
# KNOWLEDGE BASE
# ============================================================

try:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        KNOWLEDGE = json.load(f)

except Exception as e:

    print("Knowledge base error:", e)
    KNOWLEDGE = []


DOCUMENTS = [
    str(item.get("text", ""))
    for item in KNOWLEDGE
]


# ============================================================
# TF-IDF RAG
# ============================================================

if DOCUMENTS:

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10000
    )

    DOCUMENT_MATRIX = vectorizer.fit_transform(
        DOCUMENTS
    )

else:

    vectorizer = None
    DOCUMENT_MATRIX = None


def retrieve(query, top_k=3):

    if not DOCUMENTS:
        return []

    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(
        query_vector,
        DOCUMENT_MATRIX
    )[0]

    indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in indices:

        item = dict(
            KNOWLEDGE[int(index)]
        )

        item["score"] = round(
            float(scores[int(index)]),
            4
        )

        results.append(item)

    return results


# ============================================================
# AGENT
# ============================================================

def agent_plan(query):

    q = query.lower()

    tools = ["RAG"]

    numerical_words = [
        "cost",
        "price",
        "budget",
        "percentage",
        "salary",
        "roi",
        "saving",
        "score",
        "calculate",
        "how much"
    ]

    comparison_words = [
        " or ",
        " versus ",
        " vs ",
        "compare",
        "better",
        "choose",
        "should i",
        "which",
        "difference"
    ]

    if any(
        word in q
        for word in numerical_words
    ):

        tools.append("CALCULATOR")

    if any(
        word in q
        for word in comparison_words
    ):

        tools.append("DECISION_SCORER")

    tools.append("LLM")

    return tools


# ============================================================
# CONTEXT
# ============================================================

def build_context(results):

    if not results:

        return (
            "No relevant knowledge-base evidence "
            "was retrieved."
        )

    blocks = []

    for i, item in enumerate(
        results,
        1
    ):

        blocks.append(
            f"""
EVIDENCE {i}

Category:
{item.get("category", "General")}

Title:
{item.get("title", "Untitled")}

Similarity:
{item.get("score", 0):.3f}

Content:
{item.get("text", "")}
"""
        )

    return "\n-----------------------------\n".join(
        blocks
    )


# ============================================================
# SIMPLE DECISION SCORER
# ============================================================

def decision_score(query):

    q = query.lower()

    # Detect two alternatives around "or"
    match = re.search(
        r"(.+?)\s+or\s+(.+)",
        q
    )

    if not match:

        return None

    option_a = match.group(1).strip()
    option_b = match.group(2).strip()

    # Clean common question words
    option_a = re.sub(
        r"^(should i|should|can i|do i)\s+",
        "",
        option_a
    )

    option_b = re.sub(
        r"[?.!]+$",
        "",
        option_b
    )

    # If options are effectively synonyms
    cycling_words = {
        "cycling",
        "cycle",
        "cycling activity",
        "ride a cycle"
    }

    biking_words = {
        "biking",
        "bike",
        "riding a bike",
        "ride bike"
    }

    same_activity = (
        (
            any(x in option_a for x in cycling_words)
            and
            any(x in option_b for x in biking_words)
        )
        or
        (
            any(x in option_b for x in cycling_words)
            and
            any(x in option_a for x in biking_words)
        )
    )

    if same_activity:

        return {
            "option_a": option_a.title(),
            "option_b": option_b.title(),
            "score_a": 50,
            "score_b": 50,
            "same_activity": True
        }

    return {
        "option_a": option_a.title(),
        "option_b": option_b.title(),
        "score_a": 50,
        "score_b": 50,
        "same_activity": False
    }


# ============================================================
# FALLBACK
# ============================================================

def fallback_response(
    query,
    evidence,
    score_data=None
):

    if score_data:

        a = score_data["option_a"]
        b = score_data["option_b"]

        if score_data.get("same_activity"):

            recommendation = (
                f"{a} and {b} generally refer to the "
                "same activity. There is no meaningful "
                "choice between them; choose based on "
                "the equipment, route, and style you prefer."
            )

            option_a_text = (
                f"{a} is a common term for the activity."
            )

            option_b_text = (
                f"{b} is commonly used to describe the "
                "same type of activity."
            )

            tradeoffs = (
                "The main differences are terminology, "
                "regional usage, and personal preference."
            )

        else:

            recommendation = (
                f"Compare {a} and {b} using your goals, "
                "cost, accessibility, learning curve, "
                "and long-term usefulness."
            )

            option_a_text = (
                f"{a} should be evaluated against your "
                "specific requirements."
            )

            option_b_text = (
                f"{b} should be evaluated using the same "
                "criteria."
            )

            tradeoffs = (
                "The better option depends on your "
                "priorities and constraints."
            )

    elif evidence:

        recommendation = (
            "Use the retrieved decision framework and "
            "validate the choice against your specific "
            f"requirements. Strongest evidence: "
            f"{evidence[0].get('title', 'Retrieved evidence')}."
        )

        option_a_text = (
            "Evaluate the first option against the stated "
            "requirements."
        )

        option_b_text = (
            "Evaluate the alternative using the same criteria."
        )

        tradeoffs = (
            "The optimal choice depends on which criteria "
            "matter most."
        )

    else:

        recommendation = (
            "More information is required before making "
            "a reliable recommendation."
        )

        option_a_text = (
            "Evaluate the first option."
        )

        option_b_text = (
            "Evaluate the alternative."
        )

        tradeoffs = (
            "Additional context is required."
        )


    return f"""
RECOMMENDATION:

{recommendation}


KEY FACTORS:

- Personal objective
- Cost
- Accessibility
- Learning curve
- Reliability
- Long-term usefulness


OPTION A:

{option_a_text}


OPTION B:

{option_b_text}


TRADE-OFFS:

{tradeoffs}


RISKS:

The decision may change depending on the user's
specific goals, constraints, and available resources.


REASONING:

The recommendation combines the DecisionLens
decision framework with retrieved knowledge.


CONFIDENCE:

Medium
"""


# ============================================================
# GEMINI
# ============================================================

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

client = None

if API_KEY:

    try:

        client = genai.Client(
            api_key=API_KEY
        )

        print("Gemini client initialized.")

    except Exception as e:

        print(
            "Gemini initialization failed:",
            e
        )


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


# ============================================================
# FRONTEND
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/index.html")
def index():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/result.html")
def result():

    return send_from_directory(
        FRONTEND_DIR,
        "result.html"
    )


# ============================================================
# HEALTH
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({

        "status": "ok",

        "rag": bool(DOCUMENTS),

        "agent": True,

        "llm": bool(client),

        "documents": len(DOCUMENTS),

        "model": MODEL_NAME

    })


# ============================================================
# ANALYZE
# ============================================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    data = request.get_json(
        silent=True
    ) or {}

    query = str(
        data.get("query", "")
    ).strip()

    if not query:

        return jsonify({
            "error": "Decision query is required."
        }), 400


    # ========================================================
    # AGENT
    # ========================================================

    tools = agent_plan(
        query
    )


    # ========================================================
    # RAG
    # ========================================================

    evidence = retrieve(
        query,
        top_k=3
    )

    context = build_context(
        evidence
    )


    # ========================================================
    # DECISION SCORER
    # ========================================================

    score_data = None

    if "DECISION_SCORER" in tools:

        score_data = decision_score(
            query
        )


    # ========================================================
    # GEMINI PROMPT
    # ========================================================

    prompt = f"""
You are DecisionLens AI,
an intelligent decision-support system.

USER QUESTION:

{query}


AGENT TOOLS:

{", ".join(tools)}


DECISION SCORE DATA:

{json.dumps(score_data, indent=2)}


RETRIEVED KNOWLEDGE:

{context}


Your task is to give a useful decision analysis.

If the two choices are actually synonyms or
essentially the same thing, explicitly say so.

Do not manufacture facts.

Do not manufacture prices.

Do not manufacture statistics.

Use retrieved evidence where relevant.

Return exactly this structure:

RECOMMENDATION:

KEY FACTORS:

OPTION A:

OPTION B:

TRADE-OFFS:

RISKS:

REASONING:

CONFIDENCE:

Keep the answer concise and practical.
"""


    # ========================================================
    # GEMINI
    # ========================================================

    output = None

    if client:

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            output = response.text

            print(
                "Gemini response generated."
            )

        except Exception as e:

            print(
                "Gemini request failed:",
                repr(e)
            )


    # ========================================================
    # FALLBACK
    # ========================================================

    if not output:

        output = fallback_response(
            query,
            evidence,
            score_data
        )


    # ========================================================
    # RESPONSE
    # ========================================================

    return jsonify({

        "query": query,

        "recommendation": output,

        "tools_used": tools,

        "decision_score": score_data,

        "evidence": evidence

    })


# ============================================================
# START
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
        port=port
    )
