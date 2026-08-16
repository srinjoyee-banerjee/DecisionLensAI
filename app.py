# ============================================================
# DECISIONLENS AI
# AI DECISION SIMULATION & INTELLIGENCE PLATFORM
# BACKEND PART 1
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
# KNOWLEDGE BASE
# ============================================================


def load_knowledge():

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
# TEXT ENGINE
# ============================================================



STOPWORDS={

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
"between",
"or",
"vs",
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


    words=re.findall(

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


        values=[]


        for key in [

            "title",
            "topic",
            "content",
            "text",
            "summary",
            "description"

        ]:


            if item.get(key):

                values.append(

                    str(item[key])

                )


        return " ".join(values)



    return str(item)





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

        "choose",

        "pick"

    ]


    for r in remove:


        text=re.sub(

            r,

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
# INTELLIGENCE LAYER
# ============================================================


def detect_domain(question):


    text=normalize(question)


    domains={


        "technology":[

            "ai",
            "ml",
            "machine learning",
            "data science",
            "coding",
            "software"

        ],


        "career":[

            "job",
            "salary",
            "career",
            "profession"

        ],


        "education":[

            "study",
            "phd",
            "degree",
            "research"

        ],


        "creative":[

            "dance",
            "singing",
            "music",
            "art"

        ],


        "finance":[

            "money",
            "investment",
            "business"

        ]

    }



    found=[]



    for domain,words in domains.items():


        for word in words:


            if word in text:

                found.append(domain)

                break



    return found or ["general"]

# ============================================================
# USER GOAL UNDERSTANDING
# ============================================================


def detect_goals(question):


    text=normalize(question)


    goals=[]


    mapping={


        "salary":[

            "salary",
            "money",
            "income",
            "earning",
            "pay"

        ],



        "growth":[

            "future",
            "growth",
            "career",
            "opportunity",
            "long term"

        ],



        "learning":[

            "learn",
            "skill",
            "knowledge",
            "improve"

        ],



        "research":[

            "research",
            "paper",
            "phd",
            "innovation"

        ],



        "stability":[

            "stable",
            "safe",
            "security"

        ],



        "passion":[

            "love",
            "interest",
            "passion",
            "enjoy"

        ]

    }



    for goal,words in mapping.items():


        for word in words:


            if word in text:


                goals.append(goal)

                break




    if not goals:

        goals=[

            "growth",
            "future"

        ]



    return goals






# ============================================================
# OPTION PROFILE ENGINE
# ============================================================



def create_option_profile(option):


    text=normalize(option)



    profile={


        "salary":50,

        "growth":50,

        "learning":50,

        "research":50,

        "stability":50,

        "creativity":50,

        "difficulty":50


    }





    # ==========================
    # TECHNOLOGY
    # ==========================


    if any(x in text for x in [

        "machine learning",
        "ml"

    ]):


        profile.update({

            "salary":90,

            "growth":95,

            "learning":95,

            "research":95,

            "stability":80,

            "difficulty":85

        })




    elif "data science" in text:


        profile.update({

            "salary":85,

            "growth":85,

            "learning":85,

            "research":70,

            "stability":90,

            "difficulty":70

        })





    elif "python" in text:


        profile.update({

            "learning":90,

            "growth":90

        })





    # ==========================
    # CREATIVE
    # ==========================


    if any(x in text for x in [

        "dance",
        "dancing"

    ]):


        profile.update({

            "creativity":95,

            "passion":95,

            "growth":75,

            "stability":65

        })




    elif any(x in text for x in [

        "sing",

        "singing",

        "music"

    ]):


        profile.update({

            "creativity":95,

            "growth":75,

            "stability":70

        })




    return profile





# ============================================================
# DECISION MATRIX BUILDER
# ============================================================


def build_matrix(option_a,option_b):


    profile_a=create_option_profile(

        option_a

    )


    profile_b=create_option_profile(

        option_b

    )



    factors=[


        "salary",

        "growth",

        "learning",

        "research",

        "stability",

        "creativity",

        "difficulty"


    ]



    return {


        "factors":factors,


        option_a:[

            profile_a[x]

            for x in factors

        ],



        option_b:[

            profile_b[x]

            for x in factors

        ]


    }





# ============================================================
# DECISION SCORE
# ============================================================


def calculate_scores(

        option_a,

        option_b,

        goals

):


    profile_a=create_option_profile(

        option_a

    )


    profile_b=create_option_profile(

        option_b

    )



    score_a=0

    score_b=0




    for goal in goals:


        score_a += profile_a.get(

            goal,

            50

        )


        score_b += profile_b.get(

            goal,

            50

        )




    score_a/=len(goals)

    score_b/=len(goals)



    return round(score_a),round(score_b)






# ============================================================
# RISK REWARD ANALYSIS
# ============================================================



def generate_risk_reward(option):


    profile=create_option_profile(

        option

    )



    risk=max(

        20,

        100-profile["stability"]

    )



    reward=(

        profile["growth"]

        +

        profile["salary"]

    )//2



    return {


        "risk":risk,

        "reward":reward

    }





# ============================================================
# FUTURE TIMELINE GENERATOR
# ============================================================


def generate_timeline(option):


    text=normalize(option)



    if "machine" in text:


        return [

            "0-6 months: Learn ML fundamentals and build projects",

            "6-18 months: Develop AI applications",

            "2-3 years: ML Engineer / AI Specialist",

            "5 years: Senior AI Engineer or Research Engineer"

        ]




    if "data science" in text:


        return [

            "0-6 months: Statistics, Python and analytics",

            "6-18 months: Data projects and industry skills",

            "2-3 years: Data Scientist role",

            "5 years: Senior Data Scientist / Analytics Lead"

        ]




    return [

        "Short term: Build foundational skills",

        "Medium term: Gain experience",

        "Long term: Grow professionally"

    ]





# ============================================================
# FUTURE PATH DESCRIPTION
# ============================================================



def generate_future_path(option):


    text=normalize(option)



    if "machine" in text:


        return (

        "Possible future: "

        "AI Engineer, Deep Learning Engineer, "

        "Research Engineer"

        )



    if "data science" in text:


        return (

        "Possible future: "

        "Data Scientist, Analytics Lead, "

        "Business Intelligence Specialist"

        )



    return (

        "Possible future depends on skills, "

        "experience and opportunities."

    )
# ============================================================
# FINAL DECISION GENERATION
# ============================================================


def generate_analysis(
        option_a,
        option_b,
        question,
        evidence
):


    domain = detect_domain(
        question
    )


    goals = detect_goals(
        question
    )



    score_a,score_b = calculate_scores(

        option_a,

        option_b,

        goals

    )



    if score_a > score_b:


        winner = option_a

        alternative = option_b

        winning_score = score_a



    elif score_b > score_a:


        winner = option_b

        alternative = option_a

        winning_score = score_b



    else:


        winner = option_a

        alternative = option_b

        winning_score = score_a





    confidence = 70



    difference = abs(

        score_a-score_b

    )


    if difference >=10:

        confidence +=10



    if evidence:

        confidence +=10



    confidence=min(

        confidence,

        95

    )





    return {


        # ==========================
        # INTELLIGENCE SUMMARY
        # ==========================


        "decision_intelligence":{


            "domain":domain,


            "detected_goals":goals,


            "question":question


        },




        # ==========================
        # RECOMMENDATION
        # ==========================


        "recommendation":{


            "choice":winner,


            "confidence":confidence,


            "reason":

            f"{winner} better matches your goals "
            f"of {', '.join(goals)}."

        },




        # ==========================
        # DECISION MATRIX
        # ==========================


        "decision_matrix":

        build_matrix(

            option_a,

            option_b

        ),




        # ==========================
        # WHY
        # ==========================


        "why":[


            f"{winner} aligns better with your current objectives.",


            f"It provides stronger potential for "
            f"{', '.join(goals)}.",


            "The recommendation considers skills, "
            "future opportunities and trade-offs."


        ],




        "why_not":[


            f"{alternative} is still a valid path.",


            "It may become better depending on changing goals.",


            "The current recommendation reflects your stated priorities."

        ],





        # ==========================
        # ADVANTAGES
        # ==========================


        "advantages":[


            f"{winner}: stronger alignment with your goals.",


            f"{alternative}: provides different advantages."

        ],





        "disadvantages":[


            f"{winner}: may require higher commitment.",


            f"{alternative}: may have slower alignment."

        ],




        # ==========================
        # RISK REWARD
        # ==========================


        "risk_reward":{


            option_a:

            generate_risk_reward(

                option_a

            ),



            option_b:

            generate_risk_reward(

                option_b

            )

        },





        # ==========================
        # FUTURE SIMULATION
        # ==========================


        "future_paths":{


            option_a:

            generate_future_path(

                option_a

            ),



            option_b:

            generate_future_path(

                option_b

            )

        },





        "timeline":{


            winner:

            generate_timeline(

                winner

            )

        },





        "scores":{


            option_a:score_a,


            option_b:score_b

        },




        "evidence_count":

        len(evidence)


    }






# ============================================================
# MAIN ANALYZER
# ============================================================



def analyze_decision(question):


    option_a,option_b = extract_options(

        question

    )



    if not option_a or not option_b:


        return {


            "error":

            "Please provide two options. Example: Machine Learning vs Data Science"

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
# API
# ============================================================


@app.route("/api/health")

def health():


    return jsonify({


        "status":"online",


        "engine":

        "DecisionLens AI Intelligence Engine",



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
