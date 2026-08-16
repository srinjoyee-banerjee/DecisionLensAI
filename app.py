# ============================================================
# DECISIONLENS AI
# UNIVERSAL AI DECISION ADVISOR
# PERSONALIZED RAG DECISION REASONING ENGINE
# FIXED VERSION
# ============================================================


from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import os
import json
import re


# ============================================================
# APP CONFIG
# ============================================================


app = Flask(__name__)
CORS(app)


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)


KB_FILE = os.path.join(
    BASE_DIR,
    "knowledge_base.json"
)



# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================


def load_knowledge():

    if not os.path.exists(KB_FILE):
        print("Knowledge base not found")
        return []


    try:

        with open(
            KB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)



        if isinstance(data,list):
            return data



        if isinstance(data,dict):

            for key in [
                "documents",
                "knowledge",
                "entries",
                "data"
            ]:

                if key in data:
                    return data[key]


    except Exception as e:

        print(
            "KB ERROR:",
            e
        )


    return []



KB = load_knowledge()



# ============================================================
# TEXT PROCESSING
# ============================================================


STOPWORDS = {

"the",
"and",
"for",
"with",
"should",
"would",
"could",
"which",
"what",
"is",
"are",
"better",
"best",
"choose",
"choice",
"between",
"or",
"vs",
"versus",
"my",
"i",
"me",
"to",
"of",
"in",
"a",
"an"

}



def normalize(text):

    return str(text).lower().strip()



def tokenize(text):

    words = re.findall(
        r"[a-zA-Z0-9+#.-]{3,}",
        normalize(text)
    )


    return [
        w
        for w in words
        if w not in STOPWORDS
    ]



def extract_text(item):

    if isinstance(item,str):
        return item


    if isinstance(item,dict):

        parts=[]


        for key in [
            "title",
            "topic",
            "content",
            "text",
            "summary",
            "description"
        ]:

            if item.get(key):

                parts.append(
                    str(item[key])
                )


        return " ".join(parts)


    return str(item)




# ============================================================
# OPTION EXTRACTION
# ============================================================


def clean_option(text):

    text=text.strip(
        " ?.,:"
    )


    remove_patterns=[

        "should i",
        "should we",
        "which is better",
        "what is better",
        "choose",
        "pick",
        "select"

    ]


    for p in remove_patterns:

        text=re.sub(
            p,
            "",
            text,
            flags=re.I
        )


    return text.strip()




def extract_options(question):


    patterns=[

        r"(.+?)\s+vs\.?\s+(.+)",

        r"between\s+(.+?)\s+and\s+(.+)",

        r"should i\s+(.+?)\s+or\s+(.+)",

        r"(.+?)\s+or\s+(.+)"

    ]



    for pattern in patterns:


        match=re.search(
            pattern,
            question,
            re.I
        )


        if match:


            a=clean_option(
                match.group(1)
            )


            b=clean_option(
                match.group(2)
            )



            if len(a)>2 and len(b)>2:

                return a,b



    return None,None





# ============================================================
# CONTEXT DETECTION
# ============================================================


def detect_context(question):


    text=normalize(question)


    context=[]



    categories={


        "technology":[

            "python",
            "java",
            "coding",
            "software",
            "machine learning",
            "ai",
            "data science"

        ],


        "career":[

            "job",
            "career",
            "salary",
            "placement",
            "profession"

        ],


        "creative":[

            "dance",
            "sing",
            "music",
            "art",
            "creative"

        ],


        "education":[

            "study",
            "degree",
            "phd",
            "college",
            "research"

        ]

    }



    for category,words in categories.items():

        for word in words:

            if word in text:

                context.append(
                    category
                )

                break



    return context or ["general"]





# ============================================================
# PRIORITY DETECTION
# ============================================================


def detect_priorities(question):


    text=normalize(question)


    priorities=[]



    mapping={


        "growth":[

            "growth",
            "future",
            "career"

        ],


        "income":[

            "salary",
            "money",
            "income"

        ],


        "learning":[

            "learn",
            "skill",
            "knowledge"

        ],


        "passion":[

            "love",
            "passion",
            "interest",
            "happiness"

        ]

    }




    for key,words in mapping.items():

        for word in words:

            if word in text:

                priorities.append(
                    key
                )

                break



    if not priorities:

        priorities=[
            "growth",
            "future"
        ]



    return priorities
    # ============================================================
# RAG RETRIEVAL
# ============================================================


def retrieve_evidence(question):

    query=set(
        tokenize(question)
    )


    results=[]


    for item in KB:

        text=extract_text(item)

        tokens=set(
            tokenize(text)
        )


        score=len(
            query.intersection(tokens)
        )


        if score>0:

            results.append({

                "content":text,
                "score":score

            })



    results.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    return results[:5]





# ============================================================
# OPTION INTELLIGENCE SCORING
# ============================================================


def score_option(option, context, priorities):


    score=50


    text=normalize(option)



    # Technology decisions

    if "technology" in context:


        if any(x in text for x in [

            "machine learning",
            "ml",
            "ai",
            "python",
            "data science",
            "software",
            "engineering"

        ]):

            score+=20



    # Career decisions

    if "career" in context:


        if any(x in text for x in [

            "engineer",
            "developer",
            "scientist",
            "analyst"

        ]):

            score+=15



    # Creative decisions

    if "creative" in context:


        if any(x in text for x in [

            "dance",
            "sing",
            "music",
            "art"

        ]):

            score+=10



    # Priority matching

    for p in priorities:


        if p=="growth":

            score+=8


        if p=="income":

            score+=8


        if p=="learning":

            score+=6


        if p=="passion":

            score+=8



    return min(
        score,
        95
    )





# ============================================================
# DECISION GENERATOR
# ============================================================


def generate_analysis(
        option_a,
        option_b,
        question,
        evidence
):


    context=detect_context(
        question
    )


    priorities=detect_priorities(
        question
    )



    score_a=score_option(
        option_a,
        context,
        priorities
    )


    score_b=score_option(
        option_b,
        context,
        priorities
    )



    if score_a>=score_b:

        winner=option_a
        loser=option_b

        win_score=score_a

    else:

        winner=option_b
        loser=option_a

        win_score=score_b



    confidence=70


    if evidence:

        confidence+=10


    if abs(score_a-score_b)>15:

        confidence+=10



    return {


        "decision_intelligence":
        question,


        "recommendation":
        winner,


        "confidence":
        min(
            confidence,
            95
        ),


        "primary_reason":

        f"{winner} matches your detected priorities "
        f"({', '.join(priorities)}) better.",



        "why":[

            f"{winner} aligns better with your current objective.",

            f"It has stronger potential for "
            f"{', '.join(priorities)}.",

            "The recommendation considers long-term value, "
            "opportunity and practical outcomes."

        ],



        "why_not":[

            f"{loser} is still a valid option.",

            f"It may become better if your priorities change.",

            "The current limitation is lower alignment "
            "with your stated goal."

        ],



        "advantages":[

            f"{winner}: stronger alignment with your goal.",

            f"{loser}: provides alternative benefits."

        ],



        "disadvantages":[

            f"{winner} may require more commitment.",

            f"{loser} may provide slower results "
            "for this objective."

        ],



        "tradeoffs":[

            "Short-term benefit versus long-term value.",

            "Interest versus opportunity.",

            "Comfort versus growth."

        ],



        "scores":{

            option_a:score_a,

            option_b:score_b

        }

    }





# ============================================================
# MAIN ANALYSIS
# ============================================================


def analyze_decision(question):


    option_a,option_b=extract_options(
        question
    )



    if not option_a or not option_b:


        return {

            "error":
            "Please provide two options. Example: ML vs Data Science"

        }



    evidence=retrieve_evidence(
        question
    )


    result=generate_analysis(

        option_a,

        option_b,

        question,

        evidence

    )



    result["decision"]=question


    result["options"]=[

        option_a,

        option_b

    ]


    result["evidence_count"]=len(
        evidence
    )


    return result





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



@app.route("/<path:file>")
def static_files(file):

    return send_from_directory(
        FRONTEND_DIR,
        file
    )





# ============================================================
# API
# ============================================================


@app.route("/api/health")
def health():

    return jsonify({

        "status":"online",

        "engine":
        "DecisionLens AI",

        "knowledge_records":
        len(KB)

    })





@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze_api():

    try:


        data=request.get_json(
            silent=True
        ) or {}



        question=str(
            data.get(
                "decision",
                ""
            )
        ).strip()



        if len(question)<5:

            return jsonify({

                "error":
                "Please enter a decision"

            }),400




        result=analyze_decision(
            question
        )



        return jsonify(
            result
        )



    except Exception as e:


        return jsonify({

            "error":
            "Decision engine failed",

            "details":
            str(e)

        }),500





# ============================================================
# START SERVER
# ============================================================


if __name__=="__main__":


    port=int(

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
