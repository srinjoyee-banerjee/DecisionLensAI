# ============================================================
# DECISIONLENS AI
# UNIVERSAL AI DECISION ADVISOR
# RAG POWERED DECISION REASONING ENGINE
# ============================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import os
import json
import re
import random


# ============================================================
# APP CONFIGURATION
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

def load_kb():

    if not os.path.exists(KB_FILE):
        print("Knowledge base not found")
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

            for key in [
                "documents",
                "knowledge",
                "entries",
                "data"
            ]:

                if key in data:
                    return data[key]


        return []


    except Exception as e:

        print(
            "KB ERROR:",
            e
        )

        return []



KB = load_kb()



# ============================================================
# TEXT UTILITIES
# ============================================================


STOPWORDS=set([

"the",
"and",
"for",
"with",
"should",
"would",
"could",
"which",
"what",
"better",
"best",
"choose",
"option",
"between",
"or",
"vs",
"versus",
"is",
"to",
"of",
"in",
"a",
"an",
"my",
"i"

])



def normalize(text):

    return re.sub(
        r"\s+",
        " ",
        str(text)
        .lower()
        .strip()
    )



def tokenize(text):

    words=re.findall(
        r"[a-zA-Z0-9+#.-]{3,}",
        normalize(text)
    )


    return [

        w for w in words

        if w not in STOPWORDS

    ]



def extract_text(item):

    if isinstance(item,str):
        return item


    if isinstance(item,dict):

        result=[]


        for key in [
            "title",
            "topic",
            "content",
            "text",
            "description",
            "summary"
        ]:

            if item.get(key):

                result.append(
                    str(item[key])
                )


        return " ".join(result)


    return str(item)




# ============================================================
# OPTION EXTRACTION
# ============================================================


def clean_option(value):

    value=value.strip(
        " ?.,"
    )


    remove_patterns=[

        "should i",

        "should we",

        "which is better",

        "what is better",

        "choose",

        "pick"

    ]


    for pattern in remove_patterns:

        value=re.sub(
            pattern,
            "",
            value,
            flags=re.I
        )


    return value.strip()



def extract_options(question):


    patterns=[


        r"(.+?)\s+vs\.?\s+(.+)",


        r"between\s+(.+?)\s+and\s+(.+)",


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


    categories={


        "career":[

            "job",
            "career",
            "salary",
            "mba",
            "work",
            "profession"

        ],


        "technology":[

            "python",
            "java",
            "coding",
            "software",
            "programming"

        ],


        "finance":[

            "money",
            "stock",
            "invest",
            "loan",
            "house"

        ],


        "education":[

            "course",
            "degree",
            "study",
            "college",
            "master"

        ],


        "business":[

            "startup",
            "business",
            "company"

        ]

    }



    found=[]


    for category,words in categories.items():

        for word in words:

            if word in text:

                found.append(category)

                break



    return found or ["general"]





# ============================================================
# RAG RETRIEVAL
# ============================================================


def retrieve_evidence(question):


    query_tokens=set(
        tokenize(question)
    )


    results=[]



    for item in KB:


        text=extract_text(item)


        tokens=set(
            tokenize(text)
        )


        match=len(
            query_tokens.intersection(tokens)
        )


        if match>0:


            results.append({

                "text":text,

                "relevance":match

            })



    results.sort(

        key=lambda x:x["relevance"],

        reverse=True

    )


    return results[:5]
# ============================================================
# DECISIONLENS AI
# UNIVERSAL AI DECISION ADVISOR
# RAG POWERED DECISION REASONING ENGINE
# ============================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import os
import json
import re
import random


# ============================================================
# APP CONFIGURATION
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

def load_kb():

    if not os.path.exists(KB_FILE):
        print("Knowledge base not found")
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

            for key in [
                "documents",
                "knowledge",
                "entries",
                "data"
            ]:

                if key in data:
                    return data[key]


        return []


    except Exception as e:

        print(
            "KB ERROR:",
            e
        )

        return []



KB = load_kb()



# ============================================================
# TEXT UTILITIES
# ============================================================


STOPWORDS=set([

"the",
"and",
"for",
"with",
"should",
"would",
"could",
"which",
"what",
"better",
"best",
"choose",
"option",
"between",
"or",
"vs",
"versus",
"is",
"to",
"of",
"in",
"a",
"an",
"my",
"i"

])



def normalize(text):

    return re.sub(
        r"\s+",
        " ",
        str(text)
        .lower()
        .strip()
    )



def tokenize(text):

    words=re.findall(
        r"[a-zA-Z0-9+#.-]{3,}",
        normalize(text)
    )


    return [

        w for w in words

        if w not in STOPWORDS

    ]



def extract_text(item):

    if isinstance(item,str):
        return item


    if isinstance(item,dict):

        result=[]


        for key in [
            "title",
            "topic",
            "content",
            "text",
            "description",
            "summary"
        ]:

            if item.get(key):

                result.append(
                    str(item[key])
                )


        return " ".join(result)


    return str(item)




# ============================================================
# OPTION EXTRACTION
# ============================================================


def clean_option(value):

    value=value.strip(
        " ?.,"
    )


    remove_patterns=[

        "should i",

        "should we",

        "which is better",

        "what is better",

        "choose",

        "pick"

    ]


    for pattern in remove_patterns:

        value=re.sub(
            pattern,
            "",
            value,
            flags=re.I
        )


    return value.strip()



def extract_options(question):


    patterns=[


        r"(.+?)\s+vs\.?\s+(.+)",


        r"between\s+(.+?)\s+and\s+(.+)",


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


    categories={


        "career":[

            "job",
            "career",
            "salary",
            "mba",
            "work",
            "profession"

        ],


        "technology":[

            "python",
            "java",
            "coding",
            "software",
            "programming"

        ],


        "finance":[

            "money",
            "stock",
            "invest",
            "loan",
            "house"

        ],


        "education":[

            "course",
            "degree",
            "study",
            "college",
            "master"

        ],


        "business":[

            "startup",
            "business",
            "company"

        ]

    }



    found=[]


    for category,words in categories.items():

        for word in words:

            if word in text:

                found.append(category)

                break



    return found or ["general"]





# ============================================================
# RAG RETRIEVAL
# ============================================================


def retrieve_evidence(question):


    query_tokens=set(
        tokenize(question)
    )


    results=[]



    for item in KB:


        text=extract_text(item)


        tokens=set(
            tokenize(text)
        )


        match=len(
            query_tokens.intersection(tokens)
        )


        if match>0:


            results.append({

                "text":text,

                "relevance":match

            })



    results.sort(

        key=lambda x:x["relevance"],

        reverse=True

    )


    return results[:5]
{
"recommendation":"Python",

"why":[
"Python aligns better with AI ecosystem and research adoption.",
"Python matches more important factors considered.",
"The recommendation considers practicality and future relevance."
],

"why_not":[
"Java remains valuable for enterprise systems.",
"Java may be preferable where performance and large systems matter."
],

"tradeoffs":[
"Python: faster experimentation.",
"Java: stronger enterprise stability."
]
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
# HEALTH CHECK
# ============================================================


@app.route("/api/health")
def health():


    return jsonify({

        "status":

            "online",


        "service":

            "DecisionLens AI",


        "engine":

            "Universal AI Decision Advisor",


        "architecture":

            "RAG Powered Decision Reasoning",


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



        if not question:


            return jsonify({

                "error":

                "Please enter a decision."

            }),400




        if len(question)<8:


            return jsonify({

                "error":

                "Please provide more details."

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
