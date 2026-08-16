# ============================================================
# DECISIONLENS AI
# UNIVERSAL AI DECISION ADVISOR
# RAG BASED PERSONAL DECISION REASONING
# ============================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import os
import json
import re


# ============================================================
# APP
# ============================================================

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



# ============================================================
# KNOWLEDGE BASE
# ============================================================

def load_kb():

    if not os.path.exists(KB_FILE):
        return []


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
                "entries"
            ]:

                if k in data:
                    return data[k]


    except Exception as e:

        print(e)


    return []



KB=load_kb()



# ============================================================
# TEXT
# ============================================================


STOPWORDS={
"the","and","for",
"should","which",
"what","is",
"better","best",
"choose","between",
"or","vs","versus",
"i","my","to",
"a","an"
}



def clean(text):

    return re.sub(
        r"\s+",
        " ",
        str(text).lower().strip()
    )



def tokens(text):

    words=re.findall(
        r"[a-zA-Z0-9+#.-]{3,}",
        clean(text)
    )


    return [
        w for w in words
        if w not in STOPWORDS
    ]



def extract_text(item):

    if isinstance(item,str):
        return item


    if isinstance(item,dict):

        return " ".join(
            str(item.get(k,""))
            for k in [
                "title",
                "topic",
                "content",
                "text",
                "summary"
            ]
        )


    return str(item)



# ============================================================
# OPTION EXTRACTION
# ============================================================


def extract_options(question):


    patterns=[

        r"(.+?)\s+vs\.?\s+(.+)",

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

            a=m.group(1).strip(
                " ?."
            )

            b=m.group(2).strip(
                " ?."
            )


            if len(a)>2 and len(b)>2:

                return a,b


    return None,None



# ============================================================
# RAG SEARCH
# ============================================================


def retrieve(question):

    q=set(
        tokens(question)
    )


    results=[]


    for item in KB:

        text=extract_text(item)

        score=len(
            q.intersection(
                set(tokens(text))
            )
        )


        if score:

            results.append(
                {
                    "text":text,
                    "score":score
                }
            )


    results.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    return results[:3]
    # ============================================================
# DECISION REASONING ENGINE
# ============================================================


def detect_goal(question):

    q=clean(question)


    goals=[]


    mapping={

        "career":[
            "job",
            "career",
            "salary",
            "placement",
            "future"
        ],

        "learning":[
            "learn",
            "study",
            "course",
            "skill"
        ],

        "finance":[
            "money",
            "invest",
            "stock",
            "buy",
            "loan"
        ],

        "technology":[
            "code",
            "programming",
            "software",
            "python",
            "java"
        ]

    }



    for g,words in mapping.items():

        for w in words:

            if w in q:

                goals.append(g)
                break



    return goals or ["general"]





def option_strength(option,goal):


    text=clean(option)


    score=50



    # technology decisions

    if goal=="technology":

        if any(
            x in text
            for x in [
                "python",
                "ai",
                "machine learning"
            ]
        ):

            score+=25


        if "java" in text:

            score+=18



    # career decisions

    if goal=="career":

        score+=15



    # learning

    if goal=="learning":

        score+=20



    # finance

    if goal=="finance":

        score+=10



    return min(
        95,
        score
    )





def create_reasoning(
        option_a,
        option_b,
        question,
        evidence
):


    goals=detect_goal(question)


    goal=goals[0]



    score_a=option_strength(
        option_a,
        goal
    )


    score_b=option_strength(
        option_b,
        goal
    )



    if score_a>=score_b:

        winner=option_a
        loser=option_b

        win_score=score_a
        lose_score=score_b


    else:

        winner=option_b
        loser=option_a

        win_score=score_b
        lose_score=score_a




    # -------------------------------
    # HUMAN STYLE EXPLANATION
    # -------------------------------


    why=[

        f"{winner} is better aligned with your current goal ({goal}).",

        f"It provides stronger long-term value based on the context of your decision.",

        f"The choice is supported by practical considerations rather than only popularity."

    ]



    why_not=[

        f"{loser} is not a bad choice, but it has limitations for this specific objective.",

        f"It may be better when different priorities become important.",

        f"The alternative can still work depending on your constraints."

    ]



    advantages=[

        f"{winner} can provide stronger growth potential.",

        f"{winner} offers better alignment with future opportunities.",

        "It keeps more possibilities open for future decisions."

    ]



    disadvantages=[

        f"{winner} may require more effort, time or commitment.",

        "The learning curve or transition cost may be higher.",

        "Results depend on execution and consistency."

    ]



    tradeoffs=[

        f"Choosing {winner} means prioritizing long-term value over immediate convenience.",

        f"{loser} may provide some advantages that {winner} does not.",

        "The final choice depends on which factor matters most to you."

    ]



    confidence=70


    if evidence:

        confidence+=10


    if abs(
        score_a-score_b
    )>15:

        confidence+=10



    return {


        "recommendation":winner,


        "confidence":min(
            confidence,
            95
        ),


        "scores":{

            option_a:
            win_score if winner==option_a else lose_score,

            option_b:
            win_score if winner==option_b else lose_score

        },


        "why":why,


        "why_not":why_not,


        "advantages":advantages,


        "disadvantages":disadvantages,


        "tradeoffs":tradeoffs,


        "final_advice":

        (
        f"If your priority is {goal}, "
        f"I would choose {winner}. "
        f"However, reconsider {loser} if your priorities change."
        )


    }





def analyze_decision(question):


    option_a,option_b=extract_options(
        question
    )


    evidence=retrieve(
        question
    )



    if not option_a or not option_b:


        return {

            "error":
            "Please provide two options to compare. Example: Python vs Java"

        }




    result=create_reasoning(

        option_a,
        option_b,

        question,

        evidence

    )


    result["question"]=question


    result["options"]=[

        option_a,
        option_b

    ]


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
def frontend_files(file):

    return send_from_directory(
        FRONTEND_DIR,
        file
    )



# ============================================================
# HEALTH CHECK
# ============================================================


@app.route("/api/health")
def health():

    return jsonify({

        "status":"online",

        "service":
        "DecisionLens AI",

        "engine":
        "Universal Decision Reasoning Engine",

        "knowledge_records":
        len(KB)

    })



# ============================================================
# ANALYSIS API
# ============================================================


@app.route(
    "/api/analyze",
    methods=["POST"]
)
def api_analyze():


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
                "Please enter a meaningful decision."

            }),400




        result=analyze_decision(
            question
        )



        return jsonify(
            result
        )




    except Exception as e:


        print(
            "ERROR:",
            e
        )


        return jsonify({

            "error":
            "Decision engine failed.",

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
