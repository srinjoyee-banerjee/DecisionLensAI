from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import json
import os
import re


# ============================================================
# DECISIONLENS AI
# CONTEXT-AWARE DECISION ENGINE
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
# TEXT UTILITIES
# ============================================================

STOPWORDS = {
    "the", "and", "for", "with", "that", "this",
    "should", "would", "could", "from", "have",
    "will", "into", "about", "between", "which",
    "what", "when", "where", "your", "you",
    "than", "then", "they", "them", "their",
    "choose", "choice", "option", "decision",
    "better", "best", "using", "use", "want",
    "need", "like", "should", "i", "me", "my",
    "to", "of", "in", "on", "a", "an", "is",
    "or", "vs", "versus"
}


def tokenize(text):

    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}",
        text.lower()
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
            "answer"
        ]:

            value = item.get(key)

            if value:
                parts.append(str(value))

        return " ".join(parts)

    return str(item)


# ============================================================
# KNOWLEDGE RETRIEVAL
# ============================================================

def retrieve(decision, limit=5):

    decision_words = set(
        tokenize(decision)
    )

    scored = []

    for item in KNOWLEDGE_BASE:

        text = extract_text(item)

        knowledge_words = set(
            tokenize(text)
        )

        overlap = decision_words.intersection(
            knowledge_words
        )

        score = len(overlap)

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
                    "Decision Knowledge Base",

                "content":
                    str(item)
            })

    return results


# ============================================================
# DOMAIN DETECTION
# ============================================================

def detect_domain(decision):

    text = decision.lower()

    domain_keywords = {

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
            "model",
            "dataset",
            "feature engineering",
            "computer vision",
            "nlp",
            "python",
            "algorithm"
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
            "company"
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
            "higher education"
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
            "github"
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
            "enterprise"
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


    scores = {}

    for domain, keywords in domain_keywords.items():

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
# OPTION EXTRACTION
# ============================================================

def extract_options(decision):

    text = decision.strip()

    patterns = [

        r"(.+?)\s+(?:vs\.?|versus)\s+(.+)",

        r"between\s+(.+?)\s+and\s+(.+)",

        r"choose\s+(.+?)\s+or\s+(.+)",

        r"should\s+i\s+(?:choose|pick|select)\s+(.+?)\s+or\s+(.+)",

        r"(.+?)\s+or\s+(.+)"
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            option_a = match.group(1).strip()
            option_b = match.group(2).strip()


            # Remove question framing
            option_a = re.sub(
                r"^(should i|should we|which is better|what is better)\s+",
                "",
                option_a,
                flags=re.IGNORECASE
            )


            option_a = option_a.strip(
                " ?.,:"
            )

            option_b = option_b.strip(
                " ?.,:"
            )


            if (
                len(option_a) >= 2
                and len(option_b) >= 2
                and len(option_a) <= 100
                and len(option_b) <= 100
            ):

                return (
                    option_a,
                    option_b
                )


    return None, None


# ============================================================
# ML / DATA SCIENCE ANALYSIS
# ============================================================

def analyze_ml_ds(decision):

    lower = decision.lower()

    option_a, option_b = extract_options(
        decision
    )


    # --------------------------------------------------------
    # CAREER-LEVEL ML VS DATA SCIENCE
    # --------------------------------------------------------

    if (
        ("machine learning" in lower or "ml" in lower)
        and "data science" in lower
    ):

        recommendation = (
            "For a technically focused career, prioritize "
            "Machine Learning. It provides deeper exposure "
            "to model development, feature engineering, "
            "optimization and deployment. Choose Data Science "
            "instead if your priority is broader analytics, "
            "business interpretation and experimentation."
        )

        factors = [
            "Machine Learning provides deeper specialization in predictive modeling and AI systems",
            "Data Science provides broader exposure to statistics, analytics and business decision-making",
            "ML roles generally require stronger algorithmic and engineering depth",
            "Data Science roles often place greater emphasis on data analysis, experimentation and communication"
        ]

        risks = [
            "Choosing ML can require a steeper learning curve in mathematics, algorithms and model engineering",
            "Choosing Data Science may provide less specialization if your long-term goal is advanced AI engineering",
            "Both fields are highly competitive, so portfolio quality and practical experience matter"
        ]

        opportunities = [
            "Machine Learning can lead toward ML Engineer, AI Engineer and Deep Learning roles",
            "Data Science can lead toward Data Scientist, Analytics and Decision Science roles",
            "Strong ML and Data Science foundations can later overlap in applied AI projects"
        ]

        tradeoffs = [
            "Technical specialization versus broader analytics exposure",
            "Model engineering depth versus business-oriented analysis",
            "Deeper AI expertise versus greater role flexibility"
        ]

        summary = (
            "DecisionLens identified this as an ML/Data Science "
            "career decision. The key distinction is technical "
            "model-building depth versus broader analytical and "
            "business exposure."
        )

        return (
            recommendation,
            summary,
            factors,
            risks,
            opportunities,
            tradeoffs
        )


    # --------------------------------------------------------
    # MODEL COMPARISON
    # --------------------------------------------------------

    if (
        any(
            word in lower
            for word in [
                "random forest",
                "xgboost",
                "lightgbm",
                "decision tree",
                "logistic regression",
                "svm",
                "neural network"
            ]
        )
        and any(
            word in lower
            for word in [
                "model",
                "algorithm",
                "classifier",
                "prediction"
            ]
        )
    ):

        factors = [
            "Validation performance should be compared using the same train/test or cross-validation strategy",
            "Feature type, dataset size and class imbalance can strongly affect model suitability",
            "Interpretability and feature importance may matter for the final application",
            "Training and inference cost should be considered alongside accuracy"
        ]

        risks = [
            "Optimizing only for accuracy can hide poor minority-class performance",
            "A more complex model can overfit if validation is not designed carefully",
            "Model performance may change when deployed on new data"
        ]

        opportunities = [
            "Cross-validation can identify whether the performance difference is consistent",
            "Feature importance can reveal which variables actually drive predictions",
            "Model ensembles can provide stronger performance when individual models have complementary weaknesses"
        ]

        tradeoffs = [
            "Predictive performance versus interpretability",
            "Model complexity versus training and deployment simplicity",
            "Accuracy versus robustness on unseen data"
        ]

        recommendation = (
            "Choose the model that demonstrates the strongest "
            "validated performance on the metric that matters "
            "for your application, rather than selecting an "
            "algorithm based only on its reputation."
        )

        summary = (
            "DecisionLens identified this as a machine-learning "
            "model-selection decision. The analysis prioritizes "
            "validation performance, generalization, "
            "interpretability and deployment constraints."
        )

        return (
            recommendation,
            summary,
            factors,
            risks,
            opportunities,
            tradeoffs
        )


    # --------------------------------------------------------
    # GENERAL ML / AI PROJECT
    # --------------------------------------------------------

    recommendation = (
        "For an ML/AI decision, prioritize the option that "
        "produces reliable validation performance while "
        "remaining practical to train, interpret and deploy."
    )

    summary = (
        "DecisionLens identified this as an AI/ML decision. "
        "The strongest evaluation should consider data quality, "
        "model performance, generalization, computational cost "
        "and deployment requirements."
    )

    factors = [
        "Dataset quality and relevance",
        "Validation performance and generalization",
        "Feature engineering and model suitability",
        "Computational and deployment requirements"
    ]

    risks = [
        "Overfitting or weak generalization",
        "Data leakage or biased training data",
        "Performance degradation on real-world data",
        "Deployment and maintenance complexity"
    ]

    opportunities = [
        "Improved predictive performance",
        "Automation of repetitive analytical tasks",
        "Scalable AI-powered decision support",
        "Potential for future model improvement"
    ]

    tradeoffs = [
        "Accuracy versus interpretability",
        "Model complexity versus deployment simplicity",
        "Performance versus computational cost",
        "Short-term implementation versus long-term scalability"
    ]

    return (
        recommendation,
        summary,
        factors,
        risks,
        opportunities,
        tradeoffs
    )


# ============================================================
# CAREER ANALYSIS
# ============================================================

def analyze_career(decision):

    lower = decision.lower()

    option_a, option_b = extract_options(
        decision
    )


    if option_a and option_b:

        recommendation = (
            f"Between {option_a} and {option_b}, "
            f"the stronger choice depends on the skills, "
            f"role opportunities and long-term specialization "
            f"you want. Evaluate both against your target role, "
            f"salary potential, learning curve and industry demand."
        )

    else:

        recommendation = (
            "Prioritize the career path that gives you the "
            "strongest combination of relevant skills, "
            "demonstrable project experience and long-term "
            "role opportunities."
        )


    factors = [
        "Alignment with the target job role",
        "Transferable and technically relevant skills",
        "Industry demand and future career mobility",
        "Portfolio and practical experience requirements"
    ]

    risks = [
        "Changing industry requirements",
        "Skill gaps that may reduce employability",
        "Opportunity cost of specializing too early",
        "Competition for entry-level roles"
    ]

    opportunities = [
        "Building a specialized technical profile",
        "Creating projects that demonstrate practical ability",
        "Expanding into adjacent AI, software or analytical roles",
        "Developing skills that remain transferable across industries"
    ]

    tradeoffs = [
        "Specialization versus career flexibility",
        "Immediate opportunity versus long-term growth",
        "Technical depth versus breadth of skills",
        "Salary potential versus learning and role fit"
    ]

    summary = (
        "DecisionLens identified this as a career decision "
        "and evaluated it using role alignment, skill development, "
        "industry demand, flexibility and long-term growth."
    )

    return (
        recommendation,
        summary,
        factors,
        risks,
        opportunities,
        tradeoffs
    )


# ============================================================
# EDUCATION ANALYSIS
# ============================================================

def analyze_education(decision):

    recommendation = (
        "Choose the education path that most directly strengthens "
        "the expertise required for your intended career or "
        "research direction, while keeping the time and opportunity "
        "cost realistic."
    )

    summary = (
        "DecisionLens identified this as an education decision. "
        "The analysis focuses on specialization, career alignment, "
        "research value, time investment and opportunity cost."
    )

    factors = [
        "Alignment with long-term career or research goals",
        "Quality and relevance of the curriculum",
        "Research, project and industry exposure",
        "Time and financial investment"
    ]

    risks = [
        "Long time commitment",
        "Opportunity cost compared with gaining industry experience",
        "Curriculum may not match evolving industry requirements",
        "Specialization can reduce flexibility if chosen too narrowly"
    ]

    opportunities = [
        "Deeper domain expertise",
        "Research and publication opportunities",
        "Access to specialized technical networks",
        "Improved eligibility for advanced technical roles"
    ]

    tradeoffs = [
        "Academic depth versus immediate industry experience",
        "Specialization versus flexibility",
        "Long-term expertise versus short-term opportunity",
        "Research freedom versus structured career progression"
    ]

    return (
        recommendation,
        summary,
        factors,
        risks,
        opportunities,
        tradeoffs
    )


# ============================================================
# BUSINESS ANALYSIS
# ============================================================

def analyze_business(decision):

    recommendation = (
        "Prioritize the option with the clearest customer value, "
        "credible market demand and manageable execution cost. "
        "A promising opportunity should be supported by evidence "
        "rather than expected growth alone."
    )

    summary = (
        "DecisionLens identified this as a business decision and "
        "evaluated market demand, customer value, execution risk, "
        "financial exposure and scalability."
    )

    factors = [
        "Customer demand and problem severity",
        "Expected financial return",
        "Market size and competitive position",
        "Capital and execution requirements"
    ]

    risks = [
        "Market uncertainty",
        "Financial exposure",
        "Competition",
        "Execution and operational risk"
    ]

    opportunities = [
        "Revenue growth",
        "Market expansion",
        "Scalability",
        "Competitive differentiation"
    ]

    tradeoffs = [
        "Risk versus expected return",
        "Growth versus stability",
        "Capital investment versus flexibility",
        "Speed to market versus product quality"
    ]

    return (
        recommendation,
        summary,
        factors,
        risks,
        opportunities,
        tradeoffs
    )


# ============================================================
# TECHNOLOGY ANALYSIS
# ============================================================

def analyze_technology(decision):

    recommendation = (
        "Choose the technology that satisfies the current "
        "functional requirements while keeping deployment, "
        "maintenance and future scalability manageable."
    )

    summary = (
        "DecisionLens identified this as a technology decision. "
        "The analysis considers performance, ecosystem maturity, "
        "development speed, maintainability and scalability."
    )

    factors = [
        "Technical requirements and expected workload",
        "Performance and scalability",
        "Developer ecosystem and available tooling",
        "Maintenance and deployment complexity"
    ]

    risks = [
        "Vendor or framework lock-in",
        "Migration cost later",
        "Limited ecosystem or community support",
        "Complexity exceeding the actual project requirements"
    ]

    opportunities = [
        "Faster development",
        "Better scalability",
        "Access to mature libraries and tooling",
        "Improved maintainability"
    ]

    tradeoffs = [
        "Development speed versus customization",
        "Performance versus simplicity",
        "Ecosystem maturity versus flexibility",
        "Short-term implementation versus long-term maintenance"
    ]

    return (
        recommendation,
        summary,
        factors,
        risks,
        opportunities,
        tradeoffs
    )


# ============================================================
# GENERAL ANALYSIS
# ============================================================

def analyze_general(decision):

    option_a, option_b = extract_options(
        decision
    )


    if option_a and option_b:

        recommendation = (
            f"DecisionLens recommends comparing {option_a} "
            f"and {option_b} against the actual objective, "
            f"constraints, expected benefit and downside risk "
            f"rather than choosing on a single criterion."
        )

    else:

        recommendation = (
            "Prioritize the option that best satisfies the "
            "decision's primary objective while remaining "
            "realistic within your constraints and acceptable "
            "risk level."
        )


    summary = (
        "DecisionLens evaluated the decision using objective "
        "alignment, expected value, constraints, risks, "
        "opportunities and trade-offs."
    )

    factors = [
        "Alignment with the primary objective",
        "Expected value and practical impact",
        "Cost, time and resource requirements",
        "Feasibility within current constraints"
    ]

    risks = [
        "Uncertainty in future outcomes",
        "Opportunity cost",
        "Implementation or execution risk",
        "Unexpected changes in constraints"
    ]

    opportunities = [
        "Potential long-term value",
        "Future flexibility",
        "Ability to create additional opportunities",
        "Potential improvement in efficiency or outcomes"
    ]

    tradeoffs = [
        "Short-term benefit versus long-term value",
        "Risk versus potential return",
        "Flexibility versus commitment",
        "Cost versus expected benefit"
    ]

    return (
        recommendation,
        summary,
        factors,
        risks,
        opportunities,
        tradeoffs
    )


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


    # --------------------------------------------------------
    # DOMAIN-SPECIFIC ANALYSIS
    # --------------------------------------------------------

    if domain == "ml_ds":

        (
            recommendation,
            summary,
            factors,
            risks,
            opportunities,
            tradeoffs
        ) = analyze_ml_ds(decision)


    elif domain == "career":

        (
            recommendation,
            summary,
            factors,
            risks,
            opportunities,
            tradeoffs
        ) = analyze_career(decision)


    elif domain == "education":

        (
            recommendation,
            summary,
            factors,
            risks,
            opportunities,
            tradeoffs
        ) = analyze_education(decision)


    elif domain == "business":

        (
            recommendation,
            summary,
            factors,
            risks,
            opportunities,
            tradeoffs
        ) = analyze_business(decision)


    elif domain == "technology":

        (
            recommendation,
            summary,
            factors,
            risks,
            opportunities,
            tradeoffs
        ) = analyze_technology(decision)


    else:

        (
            recommendation,
            summary,
            factors,
            risks,
            opportunities,
            tradeoffs
        ) = analyze_general(decision)


    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence = 68

    if domain != "general":
        confidence += 8

    if retrieved:
        confidence += 6

    if len(decision.split()) >= 12:
        confidence += 5

    confidence = min(
        confidence,
        94
    )


    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "decision":
            decision,

        "domain":
            domain,

        "recommendation":
            recommendation,

        "summary":
            summary,

        "confidence":
            confidence,

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
# API HEALTH
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({

        "status":
            "online",

        "service":
            "DecisionLens AI",

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
