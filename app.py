# ============================================================
# DECISIONLENS AI
# UNIVERSAL AI DECISION ADVISOR
# PERSONALIZED RAG DECISION REASONING ENGINE
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
        print("Knowledge base missing")
        return []


    try:

        with open(
            KB_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)



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
"option",
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

    return re.sub(
        r"\s+",
        " ",
        str(text)
        .lower()
        .strip()
    )



def tokenize(text):

    words = re.findall(
        r"[a-zA-Z0-9+#.-]{3,}",
        normalize(text)
    )


    return [

        word

        for word in words

        if word not in STOPWORDS

    ]




def extract_text(item):

    if isinstance(item,str):

        return item



    if isinstance(item,dict):

        content=[]


        for key in [

            "title",
            "topic",
            "content",
            "text",
            "summary",
            "description"

        ]:

            if item.get(key):

                content.append(
                    str(item[key])
                )


        return " ".join(content)



    return str(item)





# ============================================================
# OPTION EXTRACTION
# ============================================================


def clean_option(text):

    text=text.strip(
        " ?.,:"
    )


    remove=[

        "should i",
        "should we",
        "which is better",
        "what is better",
        "choose",
        "pick",
        "select"

    ]


    for item in remove:

        text=re.sub(
            item,
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


            if (
                len(a)>2
                and
                len(b)>2
            ):

                return a,b



    return None,None





# ============================================================
# DECISION CONTEXT
# ============================================================


def detect_context(question):


    text=normalize(question)


    contexts=[]


    categories={


        "career":[

            "job",
            "career",
            "salary",
            "role",
            "placement",
            "profession"

        ],



        "education":[

            "phd",
            "degree",
            "master",
            "college",
            "study",
            "research"

        ],



        "technology":[

            "python",
            "java",
            "software",
            "coding",
            "programming",
            "framework"

        ],



        "finance":[

            "money",
            "investment",
            "stock",
            "buy",
            "loan",
            "return"

        ],



        "business":[

            "startup",
            "business",
            "company",
            "product"

        ]

    }




    for category,words in categories.items():


        for word in words:


            if word in text:

                contexts.append(
                    category
                )

                break



    return contexts or ["general"]





# ============================================================
# USER PRIORITY DETECTION
# ============================================================


def detect_priorities(question):


    text=normalize(question)


    priorities=[]


    mapping={


        "growth":[

            "growth",
            "future",
            "career",
            "long term"

        ],



        "income":[

            "salary",
            "money",
            "income",
            "pay"

        ],



        "learning":[

            "learn",
            "skill",
            "knowledge",
            "research"

        ],



        "stability":[

            "safe",
            "stable",
            "security"

        ],



        "flexibility":[

            "flexible",
            "options",
            "freedom"

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
            "learning",
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
# DECISION REASONING ENGINE
# ============================================================


def compare_option(option, priorities, context):

    score = 50

    text = normalize(option)


    for priority in priorities:


        if priority == "growth":

            score += 10


        if priority == "learning":

            score += 8


        if priority == "income":

            score += 7


        if priority == "stability":

            score += 5


        if priority == "flexibility":

            score += 6



    # domain signals

    if "technology" in context:


        if any(
            word in text
            for word in [
                "python",
                "ai",
                "machine learning",
                "cloud"
            ]
        ):

            score += 12



    if "career" in context:


        if any(
            word in text
            for word in [
                "engineer",
                "job",
                "role",
                "developer"
            ]
        ):

            score += 10



    if "education" in context:


        if any(
            word in text
            for word in [
                "phd",
                "research",
                "degree"
            ]
        ):

            score += 10



    return min(
        95,
        score
    )





def generate_analysis(
        option_a,
        option_b,
        question,
        evidence
):


    context = detect_context(
        question
    )


    priorities = detect_priorities(
        question
    )



    score_a = compare_option(
        option_a,
        priorities,
        context
    )


    score_b = compare_option(
        option_b,
        priorities,
        context
    )



    if score_a >= score_b:

        winner = option_a
        alternative = option_b

    else:

        winner = option_b
        alternative = option_a




    return {


        "recommendation":winner,


        "summary":
        (
            f"Based on your goal, priorities and "
            f"decision context, {winner} appears "
            f"to be the better fit compared with "
            f"{alternative}."
        ),



        "why":[

            f"{winner} aligns better with your current priorities.",

            f"It provides stronger potential for "
            f"{', '.join(priorities)}.",

            "The recommendation considers practical outcomes, "
            "future opportunities and your stated situation."

        ],



        "why_not":[

            f"{alternative} is still a valid option.",

            f"It may be better if your priority changes "
            f"towards different goals.",

            "The limitation is that it may not match "
            "your current objective as strongly."

        ],



        "advantages":[

            f"{winner} advantage: stronger alignment "
            "with your current direction.",

            f"{alternative} advantage: offers different "
            "benefits that may matter in another situation."

        ],



        "disadvantages":[

            f"{winner} may require more commitment, "
            "effort or adjustment.",

            f"{alternative} may have slower alignment "
            "with your current goal."

        ],



        "tradeoffs":[

            f"You are choosing between the strengths of "
            f"{winner} and the benefits of {alternative}.",

            "The main trade-off is immediate benefit "
            "versus long-term value.",

            "The best choice depends on which outcome "
            "matters most to you."

        ],



        "final_advice":
        (
            f"If your main objective is {priorities[0]}, "
            f"I would lean towards {winner}. "
            f"However, reconsider {alternative} if "
            "your priorities change."
        ),



        "scores":{

            option_a:score_a,

            option_b:score_b

        },


        "confidence":

        min(
            95,
            70 + (10 if evidence else 0)
        )

    }






def analyze_decision(question):


    option_a,option_b = extract_options(
        question
    )


    if not option_a or not option_b:


        return {

            "error":
            "Please provide two options. Example: Python vs Java"

        }



    evidence = retrieve_evidence(
        question
    )



    result = generate_analysis(

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


    result["evidence"]=evidence


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
def files(file):

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
        "Personal AI Decision Advisor",

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
                "Please enter a decision."

            }),400




        result=analyze_decision(
            question
        )



        return jsonify(
            result
        )



    except Exception as e:


        print(
            "ENGINE ERROR:",
            e
        )


        return jsonify({

            "error":
            "Decision engine failed.",

            "details":
            str(e)

        }),500





# ============================================================
# START
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
