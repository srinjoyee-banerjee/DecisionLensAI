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
except Exception:
    KNOWLEDGE = []


DOCUMENTS = [
    str(item.get("text", ""))
    for item in KNOWLEDGE
]


# ============================================================
# LIGHTWEIGHT RAG
# TF-IDF instead of SentenceTransformer
# This avoids Torch/CUDA and keeps Render memory low.
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

    if not DOCUMENTS or vectorizer is None:
        return []

    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(
        query_vector,
        DOCUMENT_MATRIX
    )[0]

    indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in indices:

        item = dict(KNOWLEDGE[int(index)])

        item["score"] = round(
            float(scores[int(index)]),
            4
        )

        results.append(item)

    return results


# ============================================================
# AGENT PLANNER
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
        "which"
    ]

    if any(word in q for word in numerical_words):
        tools.append("CALCULATOR")

    if any(word in q for word in comparison_words):
        tools.append("DECISION_SCORER")

    tools.append("LLM")

    return tools


# ============================================================
# CONTEXT
# ============================================================

def build_context(results):

    if not results:
        return "No relevant knowledge-base evidence was retrieved."

    context_parts = []

    for i, item in enumerate(results, 1):

        context_parts.append(
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

-----------------------------
"""
        )

    return "\n".join(context_parts)


# ============================================================
# FALLBACK RESPONSE
# ============================================================

def fallback_response(query, evidence):

    if evidence:

        strongest = evidence[0].get(
            "title",
            "Retrieved evidence"
        )

        recommendation = (
            "Use the retrieved decision framework and "
            "validate the choice against your specific "
            f"requirements. Strongest evidence: {strongest}."
        )

    else:

        recommendation = (
            "More project-specific information is required "
            "before making a reliable recommendation."
        )

    return f"""
RECOMMENDATION:

{recommendation}


KEY FACTORS:

- Requirements
- Cost
- Reliability
- Scalability
- Available expertise
- Execution risk


OPTION A:

Evaluate the first option against the stated requirements.


OPTION B:

Evaluate the alternative using the same criteria.


TRADE-OFFS:

The optimal choice depends on which criteria matter most.


RISKS:

Limited project-specific information may change the result.


REASONING:

The recommendation is grounded in the DecisionLens knowledge base.


CONFIDENCE:

Medium
"""


# ============================================================
# GEMINI
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:

    try:
        client = genai.Client(
            api_key=API_KEY
        )
    except Exception:
        client = None


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


# ============================================================
# FRONTEND ROUTES
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
        "documents": len(DOCUMENTS)
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


    # ----------------------------------------
    # AGENT
    # ----------------------------------------

    tools = agent_plan(query)


    # ----------------------------------------
    # RAG
    # ----------------------------------------

    evidence = retrieve(
        query,
        top_k=3
    )

    context = build_context(
        evidence
    )


    # ----------------------------------------
    # PROMPT
    # ----------------------------------------

    prompt = f"""
You are DecisionLens AI.

You are an agentic decision-support system
using Retrieval Augmented Generation.

USER DECISION:

{query}


TOOLS SELECTED:

{", ".join(tools)}


RETRIEVED KNOWLEDGE:

{context}


Analyze the decision using the retrieved knowledge.

Return exactly:

RECOMMENDATION:

KEY FACTORS:

OPTION A:

OPTION B:

TRADE-OFFS:

RISKS:

REASONING:

CONFIDENCE:


RULES:

- Use retrieved evidence where relevant.
- Do not invent evidence.
- Do not invent prices.
- Do not invent statistics.
- Clearly state assumptions.
- Give a balanced recommendation.
- Keep the answer concise.
"""


    # ----------------------------------------
    # GEMINI
    # ----------------------------------------

    output = None

    if client:

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            output = response.text

        except Exception as e:

            print(
                "Gemini error:",
                str(e)
            )


    # ----------------------------------------
    # FALLBACK
    # ----------------------------------------

    if not output:

        output = fallback_response(
            query,
            evidence
        )


    # ----------------------------------------
    # RESPONSE
    # ----------------------------------------

    return jsonify({

        "query": query,

        "recommendation": output,

        "tools_used": tools,

        "evidence": evidence

    })


# ============================================================
# RENDER START
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
