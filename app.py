
import os
import json

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import numpy as np
from sentence_transformers import SentenceTransformer
from google import genai


# ============================================================
# CONFIGURATION
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
# LOAD KNOWLEDGE BASE
# ============================================================

with open(KB_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)


# ============================================================
# EMBEDDING MODEL
# ============================================================

embedder = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

DOCUMENTS = [
    item["text"]
    for item in KNOWLEDGE
]

DOCUMENT_EMBEDDINGS = embedder.encode(
    DOCUMENTS,
    normalize_embeddings=True,
    show_progress_bar=False
)


# ============================================================
# GEMINI
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    client = genai.Client(
        api_key=API_KEY
    )
else:
    client = None


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve(query, top_k=3):

    query_embedding = embedder.encode(
        [query],
        normalize_embeddings=True
    )[0]

    scores = np.dot(
        DOCUMENT_EMBEDDINGS,
        query_embedding
    )

    indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in indices:

        item = dict(
            KNOWLEDGE[int(index)]
        )

        item["score"] = float(
            scores[int(index)]
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
# BUILD RAG CONTEXT
# ============================================================

def build_context(results):

    context = ""

    for i, item in enumerate(
        results,
        1
    ):

        context += f"""
EVIDENCE {i}

Category:
{item["category"]}

Title:
{item["title"]}

Similarity:
{item["score"]:.3f}

Content:
{item["text"]}

-----------------------------
"""

    return context


# ============================================================
# FALLBACK
# ============================================================

def fallback_response(
    query,
    evidence
):

    if evidence:

        strongest = evidence[0]["title"]

        recommendation = (
            "Use the retrieved decision framework and "
            "validate the choice against your specific "
            f"requirements. Strongest evidence: {strongest}."
        )

    else:

        recommendation = (
            "More information is required before making "
            "a reliable recommendation."
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

The recommendation is grounded in the retrieved DecisionLens knowledge base.


CONFIDENCE:

Medium
"""


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():

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


@app.route("/api/health")
def health():

    return jsonify({
        "status": "ok",
        "rag": True,
        "agent": True,
        "llm": bool(client)
    })


# ============================================================
# MAIN AI ENDPOINT
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


    # --------------------------------
    # AGENT
    # --------------------------------

    tools = agent_plan(
        query
    )


    # --------------------------------
    # RAG
    # --------------------------------

    evidence = retrieve(
        query,
        top_k=3
    )

    context = build_context(
        evidence
    )


    # --------------------------------
    # LLM PROMPT
    # --------------------------------

    prompt = f"""
You are DecisionLens AI.

You are an agentic decision-support system
using Retrieval Augmented Generation.

USER DECISION:

{query}


TOOLS SELECTED BY AGENT:

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

- Use retrieved evidence.
- Do not invent evidence.
- Do not invent prices.
- Do not invent statistics.
- Clearly state assumptions.
- Give a balanced recommendation.
- Keep the answer concise.
"""


    # --------------------------------
    # GEMINI
    # --------------------------------

    if client:

        try:

            response = client.interactions.create(
                model=MODEL_NAME,
                input=prompt
            )

            output = response.output_text

        except Exception:

            output = fallback_response(
                query,
                evidence
            )

    else:

        output = fallback_response(
            query,
            evidence
        )


    # --------------------------------
    # RESPONSE
    # --------------------------------

    return jsonify({

        "query": query,

        "recommendation": output,

        "tools_used": tools,

        "evidence": evidence

    })


# ============================================================
# LOCAL / RENDER START
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
