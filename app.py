```python
import os
import json

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

KB_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base.json"
)


app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

CORS(app)


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

try:

    with open(
        KB_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        KNOWLEDGE = json.load(f)

except Exception as e:

    print(
        f"WARNING: Could not load knowledge base: {e}"
    )

    KNOWLEDGE = []


# ============================================================
# LIGHTWEIGHT RAG
# ============================================================
# Uses TF-IDF instead of SentenceTransformers.
#
# This avoids:
# - PyTorch
# - CUDA
# - NVIDIA packages
# - Large embedding models
#
# This is much more suitable for Render's
# low-memory instances.
# ============================================================

DOCUMENTS = [
    str(item.get("text", ""))
    for item in KNOWLEDGE
]


if DOCUMENTS:

    vectorizer = TfidfVectorizer(
        lowercase=True,
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


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if API_KEY:

    try:

        client = genai.Client(
            api_key=API_KEY
        )

    except Exception as e:

        print(
            f"WARNING: Gemini client initialization failed: {e}"
        )

        client = None

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

    if (
        not KNOWLEDGE
        or vectorizer is None
        or DOCUMENT_MATRIX is None
    ):

        return []


    try:

        query_vector = vectorizer.transform(
            [query]
        )

        scores = cosine_similarity(
            query_vector,
            DOCUMENT_MATRIX
        )[0]

    except Exception as e:

        print(
            f"RAG retrieval error: {e}"
        )

        return []


    # Get highest scoring documents

    indices = scores.argsort()[::-1]

    results = []

    for index in indices:

        score = float(
            scores[index]
        )

        # Ignore completely unrelated documents

        if score <= 0:
            continue

        item = dict(
            KNOWLEDGE[int(index)]
        )

        item["score"] = round(
            score,
            4
        )

        results.append(
            item
        )

        if len(results) >= top_k:
            break


    return results


# ============================================================
# AGENT PLANNER
# ============================================================

def agent_plan(query):

    q = query.lower()

    tools = [
        "RAG"
    ]


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

        tools.append(
            "CALCULATOR"
        )


    if any(
        word in q
        for word in comparison_words
    ):

        tools.append(
            "DECISION_SCORER"
        )


    tools.append(
        "LLM"
    )


    return tools


# ============================================================
# BUILD RAG CONTEXT
# ============================================================

def build_context(results):

    if not results:

        return (
            "No relevant evidence was retrieved "
            "from the DecisionLens knowledge base."
        )


    context_parts = []


    for i, item in enumerate(
        results,
        1
    ):

        category = item.get(
            "category",
            "General"
        )

        title = item.get(
            "title",
            "Untitled"
        )

        text = item.get(
            "text",
            ""
        )

        score = item.get(
            "score",
            0
        )


        context_parts.append(
            f"""
EVIDENCE {i}

Category:
{category}

Title:
{title}

Relevance:
{score:.3f}

Content:
{text}

-----------------------------
"""
        )


    return "\n".join(
        context_parts
    )


# ============================================================
# FALLBACK RESPONSE
# ============================================================

def fallback_response(
    query,
    evidence
):

    if evidence:

        strongest = evidence[0].get(
            "title",
            "Retrieved evidence"
        )

        recommendation = (
            "Use the retrieved decision framework "
            "and validate the choice against your "
            f"specific requirements. Strongest evidence: "
            f"{strongest}."
        )

    else:

        recommendation = (
            "More information is required before "
            "making a reliable recommendation."
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
# FRONTEND ROUTES
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/index.html")
def index_page():

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
# FRONTEND STATIC FILES
# ============================================================

@app.route("/<path:filename>")
def frontend_files(
    filename
):

    file_path = os.path.join(
        FRONTEND_DIR,
        filename
    )


    if os.path.isfile(
        file_path
    ):

        return send_from_directory(
            FRONTEND_DIR,
            filename
        )


    return jsonify({
        "error": "File not found"
    }), 404


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({

        "status": "ok",

        "rag": True,

        "retrieval": "TF-IDF",

        "agent": True,

        "llm": bool(client),

        "knowledge_documents": len(
            KNOWLEDGE
        )

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
        data.get(
            "query",
            ""
        )
    ).strip()


    if not query:

        return jsonify({

            "error":
                "Decision query is required."

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
    # LLM PROMPT
    # ========================================================

    prompt = f"""
You are DecisionLens AI.

You are an intelligent decision-support system
using Retrieval Augmented Generation.

USER DECISION:

{query}


TOOLS SELECTED BY AGENT:

{", ".join(tools)}


RETRIEVED KNOWLEDGE:

{context}


Analyze the user's decision using the retrieved
knowledge.

Return exactly the following sections:

RECOMMENDATION:

KEY FACTORS:

OPTION A:

OPTION B:

TRADE-OFFS:

RISKS:

REASONING:

CONFIDENCE:


RULES:

- Use retrieved evidence whenever relevant.
- Do not invent evidence.
- Do not invent prices.
- Do not invent statistics.
- Clearly state assumptions.
- Give a balanced recommendation.
- Keep the response concise.
- If the knowledge base does not contain enough
  information, clearly say so.
"""


    # ========================================================
    # GEMINI
    # ========================================================

    if client:

        try:

            response = client.interactions.create(

                model=MODEL_NAME,

                input=prompt

            )


            output = response.output_text


        except Exception as e:

            print(
                f"Gemini error: {e}"
            )

            output = fallback_response(
                query,
                evidence
            )

    else:

        output = fallback_response(
            query,
            evidence
        )


    # ========================================================
    # RESPONSE
    # ========================================================

    return jsonify({

        "query": query,

        "recommendation": output,

        "tools_used": tools,

        "evidence": evidence

    })


# ============================================================
# ERROR HANDLER
# ============================================================

@app.errorhandler(500)
def internal_error(error):

    return jsonify({

        "error":
            "Internal server error.",

        "details":
            str(error)

    }), 500


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
```
