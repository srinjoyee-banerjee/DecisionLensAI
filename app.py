from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import os
import json
import re
import math


# =====================================================
# DECISIONLENS AI
# UNIVERSAL DECISION INTELLIGENCE ENGINE
# =====================================================


app = Flask(__name__)
CORS(app)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

KB_FILE = os.path.join(
    BASE_DIR,
    "knowledge_base.json"
)



# =====================================================
# LOAD KNOWLEDGE BASE
# =====================================================


def load_kb():

    try:

        with open(
            KB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data=json.load(f)


        if isinstance(data,list):
            return data

        if isinstance(data,dict):

            for k in [
                "documents",
                "knowledge",
                "data",
                "items"
            ]:

                if k in data:
                    return data[k]


        return []


    except Exception:

        return []



KB = load_kb()



# =====================================================
# TEXT PROCESSING
# =====================================================


STOPWORDS={
"the","is","a","an","to",
"for","and","or","should",
"i","my","me","which",
"better","best","choose",
"between","vs","versus"
}



def clean(text):

    return re.sub(
        r"\s+",
        " ",
        str(text).lower()
    ).strip()



def tokens(text):

    words=re.findall(
        r"[a-zA-Z0-9+#.-]{3,}",
        clean(text)
    )

    return [
        w for w in words
        if w not in STOPWORDS
    ]



# =====================================================
# UNIVERSAL OPTION EXTRACTION
# =====================================================


def extract_options(question):


    patterns=[

        r"(.+?)\s+vs\s+(.+)",

        r"(.+?)\s+versus\s+(.+)",

        r"between\s+(.+?)\s+and\s+(.+)",

        r"should i\s+(.+?)\s+or\s+(.+)",

        r"(.+?)\s+or\s+(.+)"


    ]


    for p in patterns:

        m=re.search(
            p,
            question,
            re.I
        )


        if m:

            a=m.group(1)
            b=m.group(2)


            a=re.sub(
                r"^(choose|pick|take)\s+",
                "",
                a,
                flags=re.I
            )


            return (
                a.strip(" ?"),
                b.strip(" ?")
            )


    return None,None



# =====================================================
# RAG RETRIEVAL
# =====================================================


def retrieve(question):


    q=set(tokens(question))

    results=[]


    for doc in KB:


        text=json.dumps(
            doc
        ).lower()


        score=0


        for word in q:

            if word in text:
                score+=1


        if score:


            results.append(
                {
                "content":text[:500],
                "score":score
                }
            )



    results.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    return results[:5]



# =====================================================
# UNIVERSAL DECISION FACTORS
# =====================================================


FACTORS=[

"cost",

"time requirement",

"learning difficulty",

"future growth",

"risk",

"flexibility",

"practical usefulness",

"long term value"

]



# =====================================================
# DYNAMIC SCORING
# =====================================================


def score_option(option,question,evidence):


    text=clean(question)

    score=70


    opt=clean(option)


    # evidence influence

    for e in evidence:

        if opt in e["content"]:
            score+=5



    # keyword intelligence

    positive={

        "future":10,

        "career":10,

        "growth":8,

        "stable":8,

        "easy":5,

        "cheap":5,

        "demand":8,

        "popular":5

    }



    negative={

        "risk":-5,

        "expensive":-5,

        "difficult":-3

    }



    for k,v in positive.items():

        if k in text:
            score+=v



    for k,v in negative.items():

        if k in text:
            score+=v



    # option complexity

    score += min(
        10,
        len(option.split())
    )



    return round(
        max(40,min(score,98)),
        1
    )



# =====================================================
# GENERATE REPORT
# =====================================================


def analyze(question):


    option1,option2=extract_options(
        question
    )


    evidence=retrieve(
        question
    )



    if not option1 or not option2:


        return {

        "confidence":55,

        "recommendation":
        "DecisionLens requires two comparable options. Try asking with 'A vs B' format.",

        "evidence":evidence

        }



    score1=score_option(
        option1,
        question,
        evidence
    )


    score2=score_option(
        option2,
        question,
        evidence
    )



    winner=(
        option1
        if score1>=score2
        else option2
    )



    confidence=65


    if evidence:
        confidence+=10


    if abs(score1-score2)>10:
        confidence+=10



    return {


    "decision":question,


    "options":[
        option1,
        option2
    ],


    "recommended_option":
        winner,


    "confidence":
        min(confidence,95),


    "option_scores":{

        option1:score1,

        option2:score2

    },


    "recommendation":

    f"""
DecisionLens recommends {winner}.

Scores:
{option1}: {score1}/100
{option2}: {score2}/100

The recommendation considers:
- objective alignment
- feasibility
- future value
- risk
- available evidence

This decision should be revisited if priorities change.
""",


    "factors":FACTORS,


    "risks":[

    "Future conditions may change",

    "Limited evidence can affect confidence",

    "Execution quality influences outcomes"

    ],


    "opportunities":[

    "Potential growth",

    "Skill improvement",

    "Better long-term positioning"

    ],


    "tradeoffs":[

    f"{option1} vs {option2}",

    "Short term benefit vs long term value",

    "Risk vs reward"

    ],


    "evidence":evidence,


    "evidence_count":len(evidence)


    }



# =====================================================
# ROUTES
# =====================================================


@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )



@app.route("/<path:file>")
def files(file):

    return send_from_directory(
        FRONTEND_DIR,
        file
    )



@app.route(
"/api/analyze",
methods=["POST"]
)
def api():


    data=request.json


    question=data.get(
        "decision",
        ""
    )


    if len(question)<5:

        return jsonify(
        {
        "error":"Enter a valid decision"
        }),400



    return jsonify(
        analyze(question)
    )



@app.route("/api/health")
def health():

    return jsonify({

    "status":"online",

    "engine":
    "Universal Decision Intelligence",

    "knowledge":
    len(KB)

    })



if __name__=="__main__":


    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
               5000
            )
        )
    )
