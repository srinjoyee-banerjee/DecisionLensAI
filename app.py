from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import json
import os
import re
import math


# ============================================================
# DECISIONLENS AI
# RAG-POWERED DECISION INTELLIGENCE ENGINE
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
        print("Knowledge base not found:", KB_FILE)
        return []

    try:
        with open(KB_FILE, "r", encoding="utf-8") as file:
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
# STOPWORDS
# ============================================================

STOPWORDS = {
    "the", "and", "for", "with", "that", "this",
    "should", "would", "could", "from", "have",
    "will", "into", "about", "between", "which",
    "what", "when", "where", "your", "you",
    "than", "then", "they", "them", "their",
    "choose", "choice", "option", "decision",
    "better", "best", "using", "use", "want",
    "need", "like", "i", "me", "my",
    "to", "of", "in", "on", "a", "an", "is",
    "or", "vs", "versus", "should", "we",
    "can", "do", "does", "would", "could"
}


# ============================================================
# TEXT UTILITIES
# ============================================================

def normalize(text):

    return re.sub(
        r"\s+",
        " ",
        str(text).lower().strip()
    )


def tokenize(text):

    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}",
        normalize(text)
    )

    return [
        word
        for word in words
        if word not in STOPWORDS
    ]


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
            "answer",
            "topic",
            "category"
        ]:

            value = item.get(key)

            if value:
                parts.append(str(value))

        return " ".join(parts)

    return str(item)


# ============================================================
# OPTION EXTRACTION
# ============================================================

def clean_option(option):

    option = option.strip(" ?.,:;")

    option = re.sub(
        r"^(should i|should we|which is better|what is better)\s+",
        "",
        option,
        flags=re.IGNORECASE
    )

    option = re.sub(
        r"^(choose|pick|select)\s+",
        "",
        option,
        flags=re.IGNORECASE
    )

    return option.strip(" ?.,:;")


def extract_options(decision):

    text = decision.strip()

    patterns = [

        r"(.+?)\s+(?:vs\.?|versus)\s+(.+)",

        r"between\s+(.+?)\s+and\s+(.+)",

        r"choose\s+(.+?)\s+or\s+(.+)",

        r"should\s+i\s+(?:choose|pick|select)\s+(.+?)\s+or\s+(.+)",

        r"should\s+i\s+(?:take|do|go\s+with)\s+(.+?)\s+or\s+(.+)",

        r"(.+?)\s+or\s+(.+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        option_a = clean_option(match.group(1))
        option_b = clean_option(match.group(2))

        if (
            2 <= len(option_a) <= 120
            and 2 <= len(option_b) <= 120
        ):

            # Avoid accidentally treating a huge sentence as an option
            if len(option_a.split()) <= 15 and len(option_b.split()) <= 15:
                return option_a, option_b

    return None, None


# ============================================================
# DOMAIN DETECTION
# ============================================================

DOMAIN_KEYWORDS = {

    "ml_ds": [
        "machine learning",
        "data science",
        "data scientist",
        "ml engineer",
        "ai engineer",
        "deep learning",
        "neural network",
        "random forest",
        "xgboost",
        "classification",
        "regression",
        "dataset",
        "feature engineering",
        "computer vision",
        "nlp",
        "python",
        "algorithm",
        "model"
    ],

    "career": [
        "career",
        "job",
        "role",
        "profession",
        "salary",
        "placement",
        "employment",
        "industry",
        "company",
        "career path",
        "career option"
    ],

    "education": [
        "phd",
        "masters",
        "master's",
        "degree",
        "college",
        "university",
        "course",
        "study",
        "research",
        "higher education",
        "certification"
    ],

    "technology": [
        "software",
        "framework",
        "technology",
        "database",
        "cloud",
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "react",
        "flask",
        "api",
        "backend",
        "frontend",
        "github",
        "python"
    ],

    "business": [
        "business",
        "startup",
        "company",
        "investment",
        "market",
        "customer",
        "revenue",
        "product",
        "enterprise",
        "profit"
    ],

    "finance": [
        "investment",
        "stock",
        "fund",
        "loan",
        "money",
        "finance",
        "financial",
        "return",
        "portfolio",
        "expense",
        "budget"
    ],

    "health": [
        "health",
        "exercise",
        "fitness",
        "diet",
        "workout",
        "nutrition",
        "sleep"
    ]
}


def detect_domain(decision):

    text = normalize(decision)

    scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in text:
                score += 1

        scores[domain] = score

    best_domain = max(
        scores,
        key=scores.get
    )

    if scores[best_domain] == 0:
        return "general"

    return best_domain


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve(decision, limit=5):

    decision_tokens = set(
        tokenize(decision)
    )

    if not decision_tokens:
        return []

    scored = []

    for item in KNOWLEDGE_BASE:

        text = extract_text(item)

        if not text:
            continue

        knowledge_tokens = set(
            tokenize(text)
        )

        overlap = decision_tokens.intersection(
            knowledge_tokens
        )

        if not overlap:
            continue

        # Basic lexical relevance
        overlap_score = len(overlap)

        # Give additional weight to important phrases
        phrase_bonus = 0

        decision_lower = normalize(decision)
        text_lower = normalize(text)

        for token in decision_tokens:

            if len(token) >= 5 and token in text_lower:
                phrase_bonus += 0.25

        score = overlap_score + phrase_bonus

        scored.append(
            (
                score,
                item,
                list(overlap)
            )
        )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    results = []

    for score, item, overlap in scored[:limit]:

        if isinstance(item, dict):

            title = item.get(
                "title",
                item.get(
                    "topic",
                    "Decision Knowledge"
                )
            )

            content = item.get(
                "content",
                item.get(
                    "text",
                    item.get(
                        "description",
                        item.get(
                            "summary",
                            ""
                        )
                    )
                )
            )

        else:

            title = "Decision Knowledge"
            content = str(item)

        results.append({

            "title": str(title),

            "content": str(content),

            "relevance":
                round(
                    min(
                        100,
                        score * 12
                    ),
                    1
                ),

            "matched_terms":
                overlap[:8]

        })

    return results


# ============================================================
# KEYWORD GROUPS FOR DECISION SCORING
# ============================================================

OBJECTIVE_TERMS = {
    "growth": [
        "growth",
        "future",
        "career",
        "long term",
        "progression",
        "advancement"
    ],

    "income": [
        "salary",
        "income",
        "pay",
        "money",
        "financial",
        "earning",
        "return"
    ],

    "skills": [
        "skill",
        "technical",
        "learning",
        "expertise",
        "knowledge",
        "experience"
    ],

    "flexibility": [
        "flexibility",
        "flexible",
        "options",
        "versatile",
        "mobility",
        "transferable"
    ],

    "risk": [
        "risk",
        "safe",
        "security",
        "stable",
        "uncertain",
        "uncertainty"
    ],

    "cost": [
        "cost",
        "price",
        "budget",
        "expensive",
        "affordable",
        "investment"
    ],

    "time": [
        "time",
        "quick",
        "fast",
        "duration",
        "years",
        "months"
    ]
}


def detect_objectives(decision):

    text = normalize(decision)

    objectives = []

    for objective, keywords in OBJECTIVE_TERMS.items():

        for keyword in keywords:

            if keyword in text:
                objectives.append(objective)
                break

    if not objectives:

        objectives = [
            "growth",
            "skills",
            "risk",
            "flexibility"
        ]

    return objectives


# ============================================================
# OPTION-SPECIFIC SIGNALS
# ============================================================

OPTION_PROFILES = {

    "machine learning": {
        "skills": 95,
        "growth": 94,
        "flexibility": 84,
        "risk": 70
    },

    "ml": {
        "skills": 95,
        "growth": 94,
        "flexibility": 84,
        "risk": 70
    },

    "ml engineer": {
        "skills": 97,
        "growth": 95,
        "flexibility": 88,
        "risk": 68
    },

    "data science": {
        "skills": 90,
        "growth": 90,
        "flexibility": 92,
        "risk": 76
    },

    "data scientist": {
        "skills": 90,
        "growth": 90,
        "flexibility": 92,
        "risk": 76
    },

    "data analyst": {
        "skills": 78,
        "growth": 75,
        "flexibility": 91,
        "risk": 88
    },

    "software engineer": {
        "skills": 92,
        "growth": 92,
        "flexibility": 94,
        "risk": 78
    },

    "ai engineer": {
        "skills": 97,
        "growth": 96,
        "flexibility": 86,
        "risk": 67
    }
}


def get_profile(option):

    normalized = normalize(option)

    for name, profile in OPTION_PROFILES.items():

        if name in normalized:

            return profile

    # Generic profile
    return {
        "skills": 78,
        "growth": 78,
        "flexibility": 78,
        "risk": 78
    }


# ============================================================
# OPTION SCORING
# ============================================================

def score_option(
    option,
    decision,
    retrieved
):

    profile = get_profile(option)

    objectives = detect_objectives(
        decision
    )

    weights = {

        "growth": 1.0,

        "skills": 1.0,

        "flexibility": 0.85,

        "risk": 0.85
    }

    # Adjust weights based on actual question
    if "income" in objectives:
        weights["growth"] = 0.7
        weights["risk"] = 0.8

    if "cost" in objectives:
        weights["risk"] = 1.0

    if "time" in objectives:
        weights["flexibility"] = 0.7

    weighted_total = 0
    total_weight = 0

    for objective in objectives:

        value = profile.get(
            objective,
            75
        )

        weight = weights.get(
            objective,
            0.8
        )

        weighted_total += value * weight
        total_weight += weight

    base_score = (
        weighted_total / total_weight
        if total_weight
        else 75
    )

    # --------------------------------------------------------
    # Evidence bonus
    # --------------------------------------------------------

    option_tokens = set(
        tokenize(option)
    )

    evidence_bonus = 0

    for item in retrieved:

        evidence_text = normalize(
            item.get(
                "content",
                ""
            )
        )

        overlap = 0

        for token in option_tokens:

            if token in evidence_text:
                overlap += 1

        if overlap:
            evidence_bonus += min(
                3,
                overlap * 0.75
            )

    final_score = min(
        99,
        base_score + evidence_bonus
    )

    return round(
        final_score,
        1
    )


# ============================================================
# DYNAMIC RECOMMENDATION
# ============================================================

def build_recommendation(
    option_a,
    option_b,
    score_a,
    score_b,
    domain,
    decision
):

    difference = abs(
        score_a - score_b
    )

    if score_a > score_b:

        winner = option_a
        loser = option_b
        winner_score = score_a
        loser_score = score_b

    else:

        winner = option_b
        loser = option_a
        winner_score = score_b
        loser_score = score_a

    domain_text = {

        "ml_ds":
            "technical depth, model-building capability and long-term AI relevance",

        "career":
            "career alignment, skill development and long-term professional mobility",

        "education":
            "learning value, specialization and alignment with future goals",

        "technology":
            "technical suitability, maintainability and scalability",

        "business":
            "value creation, execution feasibility and long-term business potential",

        "finance":
            "expected value, downside risk and financial suitability",

        "health":
            "practical suitability, sustainability and potential benefit",

        "general":
            "objective alignment, feasibility, expected value and risk"
    }.get(
        domain,
        "objective alignment, feasibility and risk"
    )

    if difference >= 12:

        strength = "a clear advantage"

    elif difference >= 6:

        strength = "a meaningful advantage"

    else:

        strength = "a relatively narrow advantage"

    recommendation = (
        f"DecisionLens recommends **{winner}** over **{loser}**. "
        f"{winner} scores {winner_score}/100 compared with "
        f"{loser_score}/100, giving it {strength}. "
        f"The decision was evaluated primarily using "
        f"{domain_text}. "
        f"The result should still be reconsidered if your "
        f"constraints, priorities or available evidence change."
    )

    return recommendation, winner


# ============================================================
# DYNAMIC SUMMARY
# ============================================================

def build_summary(
    option_a,
    option_b,
    score_a,
    score_b,
    domain,
    retrieved
):

    winner = (
        option_a
        if score_a >= score_b
        else option_b
    )

    if score_a == score_b:

        comparison = (
            f"{option_a} and {option_b} produced similar "
            f"overall scores."
        )

    else:

        comparison = (
            f"{winner} produced the stronger overall score."
        )

    evidence_text = (
        f"{len(retrieved)} relevant knowledge-base "
        f"record{'s' if len(retrieved) != 1 else ''} "
        f"were retrieved."
        if retrieved
        else
        "No directly matching knowledge-base evidence "
        "was retrieved."
    )

    return (
        f"DecisionLens classified this as a {domain.replace('_', ' ')} "
        f"decision. {comparison} "
        f"The comparison combines objective alignment, "
        f"option characteristics and retrieved intelligence. "
        f"{evidence_text}"
    )


# ============================================================
# DYNAMIC FACTORS
# ============================================================

def build_factors(
    option_a,
    option_b,
    score_a,
    score_b,
    domain,
    objectives
):

    winner = (
        option_a
        if score_a >= score_b
        else option_b
    )

    factors = [

        f"Primary objective alignment favors {winner}",

        f"{option_a} scored {score_a}/100 against "
        f"{option_b} at {score_b}/100",

        "The analysis considers the priorities expressed "
        "in the decision rather than relying on a single metric",

        "Long-term suitability and practical feasibility "
        "are considered alongside potential upside"
    ]

    if "growth" in objectives:

        factors.append(
            "Long-term growth and progression were given additional weight"
        )

    if "skills" in objectives:

        factors.append(
            "Skill development and technical capability were emphasized"
        )

    if "risk" in objectives:

        factors.append(
            "Risk and uncertainty were explicitly considered"
        )

    return factors[:6]


# ============================================================
# RISKS
# ============================================================

def build_risks(
    option_a,
    option_b,
    score_a,
    score_b,
    domain
):

    return [

        f"The recommendation depends on the assumptions "
        f"contained in the decision about {option_a} and {option_b}",

        "Real-world outcomes can differ from the evidence "
        "available in the knowledge base",

        "A higher score does not eliminate execution or "
        "implementation risk",

        "Future changes in market, technology or personal "
        "constraints could change the preferred option"
    ]


# ============================================================
# OPPORTUNITIES
# ============================================================

def build_opportunities(
    option_a,
    option_b,
    winner,
    domain
):

    return [

        f"{winner} can provide stronger alignment with the "
        f"current decision objective",

        f"Combining useful capabilities from {option_a} and "
        f"{option_b} may create additional future flexibility",

        "The decision can be revisited as new evidence becomes available",

        "Additional domain-specific evidence can improve future recommendations"
    ]


# ============================================================
# TRADE-OFFS
# ============================================================

def build_tradeoffs(
    option_a,
    option_b,
    score_a,
    score_b
):

    return [

        f"{option_a}: {score_a}/100 versus "
        f"{option_b}: {score_b}/100",

        "Higher potential value may require greater effort or risk",

        "Specialization can improve depth while reducing some flexibility",

        "A short-term advantage may not always produce the strongest "
        "long-term outcome"
    ]


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(
    decision,
    option_a,
    option_b,
    score_a,
    score_b,
    retrieved
):

    difference = abs(
        score_a - score_b
    )

    confidence = 58

    # More specific decision
    if len(decision.split()) >= 8:
        confidence += 5

    if len(decision.split()) >= 15:
        confidence += 4

    # Options successfully extracted
    if option_a and option_b:
        confidence += 8

    # Evidence
    if retrieved:
        confidence += min(
            12,
            len(retrieved) * 3
        )

    # Separation between options
    if difference >= 15:
        confidence += 8

    elif difference >= 10:
        confidence += 6

    elif difference >= 5:
        confidence += 3

    confidence = max(
        50,
        min(
            95,
            confidence
        )
    )

    return int(confidence)


# ============================================================
# FALLBACK ANALYSIS
# ============================================================

def analyze_without_options(
    decision,
    domain,
    retrieved
):

    domain_name = domain.replace(
        "_",
        " "
    )

    recommendation = (
        "Prioritize the path that most directly satisfies "
        "your primary objective while remaining feasible "
        "within your available time, resources and acceptable risk."
    )

    summary = (
        f"DecisionLens classified this as a {domain_name} decision. "
        f"The analysis evaluates objective alignment, feasibility, "
        f"risk, expected value and available evidence."
    )

    factors = [

        "Alignment with the primary objective",

        "Expected practical value",

        "Time, cost and resource requirements",

        "Feasibility within current constraints",

        "Long-term sustainability"
    ]

    risks = [

        "Uncertainty in future outcomes",

        "Opportunity cost",

        "Execution or implementation risk",

        "Changes in constraints or assumptions"
    ]

    opportunities = [

        "Potential long-term value",

        "Future flexibility",

        "Additional learning or growth",

        "Improved efficiency or outcomes"
    ]

    tradeoffs = [

        "Short-term benefit versus long-term value",

        "Risk versus potential return",

        "Flexibility versus commitment",

        "Cost versus expected benefit"
    ]

    confidence = 62

    if retrieved:
        confidence += min(
            12,
            len(retrieved) * 3
        )

    return {

        "decision":
            decision,

        "domain":
            domain,

        "recommended_option":
            None,

        "confidence":
            min(
                confidence,
                90
            ),

        "option_scores":
            {},

        "recommendation":
            recommendation,

        "summary":
            summary,

        "factors":
            factors,

        "risks":
            risks,

        "opportunities":
            opportunities,

        "tradeoffs":
            tradeoffs,

        "evidence":
            retrieved,

        "evidence_count":
            len(retrieved)
    }


# ============================================================
# MAIN DECISION ENGINE
# ============================================================

def analyze_decision(decision):

    domain = detect_domain(
        decision
    )

    retrieved = retrieve(
        decision,
        limit=5
    )

    option_a, option_b = extract_options(
        decision
    )

    # --------------------------------------------------------
    # No clear two-option decision
    # --------------------------------------------------------

    if not option_a or not option_b:

        return analyze_without_options(
            decision,
            domain,
            retrieved
        )

    # --------------------------------------------------------
    # Score both options
    # --------------------------------------------------------

    score_a = score_option(
        option_a,
        decision,
        retrieved
    )

    score_b = score_option(
        option_b,
        decision,
        retrieved
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    recommendation, winner = build_recommendation(
        option_a,
        option_b,
        score_a,
        score_b,
        domain,
        decision
    )

    # --------------------------------------------------------
    # Objectives
    # --------------------------------------------------------

    objectives = detect_objectives(
        decision
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = build_summary(
        option_a,
        option_b,
        score_a,
        score_b,
        domain,
        retrieved
    )

    # --------------------------------------------------------
    # Analysis sections
    # --------------------------------------------------------

    factors = build_factors(
        option_a,
        option_b,
        score_a,
        score_b,
        domain,
        objectives
    )

    risks = build_risks(
        option_a,
        option_b,
        score_a,
        score_b,
        domain
    )

    opportunities = build_opportunities(
        option_a,
        option_b,
        winner,
        domain
    )

    tradeoffs = build_tradeoffs(
        option_a,
        option_b,
        score_a,
        score_b
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = calculate_confidence(
        decision,
        option_a,
        option_b,
        score_a,
        score_b,
        retrieved
    )

    # --------------------------------------------------------
    # Final structured result
    # --------------------------------------------------------

    return {

        "decision":
            decision,

        "domain":
            domain,

        "options": [

            option_a,

            option_b
        ],

        "recommended_option":
            winner,

        "confidence":
            confidence,

        "option_scores": {

            option_a:
                score_a,

            option_b:
                score_b
        },

        "recommendation":
            recommendation,

        "summary":
            summary,

        "factors":
            factors,

        "risks":
            risks,

        "opportunities":
            opportunities,

        "tradeoffs":
            tradeoffs,

        "evidence":
            retrieved,

        "evidence_count":
            len(retrieved),

        "objectives":
            objectives
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
# API HEALTH
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({

        "status":
            "online",

        "service":
            "DecisionLens AI",

        "engine":
            "RAG Decision Intelligence",

        "knowledge_base":
            len(KNOWLEDGE_BASE)

    })


# ============================================================
# ANALYZE API
# ============================================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        decision = str(
            data.get(
                "decision",
                ""
            )
        ).strip()

        if not decision:

            return jsonify({

                "error":
                    "Decision text is required."

            }), 400

        if len(decision) < 5:

            return jsonify({

                "error":
                    "Please provide a more detailed decision."

            }), 400

        result = analyze_decision(
            decision
        )

        return jsonify(
            result
        )

    except Exception as error:

        print(
            "ANALYSIS ERROR:",
            repr(error)
        )

        return jsonify({

            "error":
                "The decision engine encountered an error.",

            "details":
                str(error)

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
