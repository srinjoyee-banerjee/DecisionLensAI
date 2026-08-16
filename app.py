# ============================================================
# DECISIONLENS AI
# AI DECISION SIMULATION & INTELLIGENCE PLATFORM
# COMPLETE REWRITE
# PART 1/3
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
# KNOWLEDGE BASE LOADER
# ============================================================


def load_knowledge():

    if not os.path.exists(KB_FILE):

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
            "Knowledge Error:",
            e
        )


    return []



KB = load_knowledge()




# ============================================================
# TEXT UNDERSTANDING ENGINE
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
"an",
"do"

}




def normalize(text):

    return str(text).lower().strip()




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


    remove=[

        "should i",
        "should we",
        "which is better",
        "what is better",
        "choose",
        "pick"

    ]


    text=text.strip(

        " ?.,:"

    )


    for word in remove:


        text=re.sub(

            word,

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


            option_a=clean_option(

                match.group(1)

            )


            option_b=clean_option(

                match.group(2)

            )



            if len(option_a)>2 and len(option_b)>2:


                return (

                    option_a,

                    option_b

                )



    return None,None





# ============================================================
# DOMAIN UNDERSTANDING
# ============================================================



def detect_domain(question):


    text=normalize(question)



    domains={


        "technology":[

            "ai",
            "ml",
            "machine learning",
            "data science",
            "python",
            "software",
            "coding"

        ],



        "career":[

            "job",
            "career",
            "salary",
            "profession",
            "role"

        ],



        "education":[

            "study",
            "degree",
            "phd",
            "research",
            "college"

        ],



        "creative":[

            "dance",
            "sing",
            "music",
            "art"

        ],



        "finance":[

            "money",
            "investment",
            "business",
            "stock"

        ]

    }



    detected=[]



    for domain,words in domains.items():


        for word in words:


            if word in text:

                detected.append(domain)

                break




    return detected or ["general"]
    # ============================================================
# USER GOAL UNDERSTANDING ENGINE
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
            "pay",
            "package"

        ],



        "growth":[

            "future",
            "growth",
            "career",
            "opportunity",
            "long term",
            "scope"

        ],



        "learning":[

            "learn",
            "skill",
            "knowledge",
            "improve",
            "master"

        ],



        "research":[

            "research",
            "paper",
            "phd",
            "innovation",
            "scientist"

        ],



        "stability":[

            "stable",
            "safe",
            "security",
            "reliable"

        ],



        "passion":[

            "love",
            "passion",
            "interest",
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
# OPTION INTELLIGENCE PROFILE
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

        "difficulty":50,

        "risk":50


    }




    # ==========================
    # TECHNOLOGY
    # ==========================


    if any(x in text for x in [

        "machine learning",
        "ml",
        "ai"

    ]):


        profile.update({

            "salary":90,

            "growth":95,

            "learning":95,

            "research":95,

            "stability":80,

            "difficulty":85,

            "risk":40

        })





    elif "data science" in text:


        profile.update({

            "salary":88,

            "growth":85,

            "learning":85,

            "research":70,

            "stability":90,

            "difficulty":70,

            "risk":30

        })





    elif "software" in text:


        profile.update({

            "salary":90,

            "growth":90,

            "learning":85,

            "stability":85,

            "difficulty":75

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

            "growth":75,

            "passion":95,

            "stability":60,

            "risk":60

        })





    elif any(x in text for x in [

        "sing",
        "singing",
        "music"

    ]):


        profile.update({

            "creativity":95,

            "growth":75,

            "passion":95,

            "stability":65,

            "risk":55

        })





    # ==========================
    # EDUCATION
    # ==========================


    if "phd" in text or "research" in text:


        profile.update({

            "research":95,

            "learning":95,

            "growth":85

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

        "difficulty",

        "risk"

    ]



    return {


        "labels":factors,


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
# DECISION CALCULATION ENGINE
# ============================================================



def calculate_scores(option_a,option_b,goals):


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



    return {


        "risk":

        profile["risk"],



        "reward":

        round(

            (

            profile["growth"]

            +

            profile["salary"]

            )/2

        )

    }






# ============================================================
# FUTURE SIMULATION TIMELINE
# ============================================================



def generate_timeline(option):


    text=normalize(option)



    if "machine" in text:


        return [

            "0-6 months: Learn ML algorithms, Python and projects",

            "6-18 months: Build AI applications",

            "2-3 years: ML Engineer / AI Specialist",

            "5 years: Senior AI Engineer / Research Engineer"

        ]





    if "data science" in text:


        return [

            "0-6 months: Statistics, SQL and analytics",

            "6-18 months: Real-world data projects",

            "2-3 years: Data Scientist role",

            "5 years: Analytics Lead"

        ]





    return [

        "Short term: Build skills",

        "Medium term: Gain experience",

        "Long term: Professional growth"

    ]







# ============================================================
# FUTURE PATH GENERATOR
# ============================================================



def generate_future_path(option):


    text=normalize(option)



    if "machine" in text:


        return [

            "AI Engineer",

            "Deep Learning Engineer",

            "Research Scientist"

        ]



    if "data science" in text:


        return [

            "Data Scientist",

            "ML Analyst",

            "Analytics Lead"

        ]



    if "dance" in text:


        return [

            "Performer",

            "Choreographer",

            "Creative Director"

        ]



    if "sing" in text:


        return [

            "Singer",

            "Composer",

            "Music Producer"

        ]



    return [

        "Skill Development",

        "Experience",

        "Career Growth"

    ]






# ============================================================
# VISUAL INTELLIGENCE ENGINE
# ============================================================



def generate_visual_context(domain):


    main=domain[0]



    visuals={


        "technology":{

            "image":
            "https://images.unsplash.com/photo-1518770660439-4636190af475",

            "title":
            "Technology Intelligence",

            "theme":
            "AI, software and innovation"

        },



        "career":{

            "image":
            "https://images.unsplash.com/photo-1521737604893-d14cc237f11d",

            "title":
            "Career Intelligence",

            "theme":
            "Opportunity and professional growth"

        },



        "creative":{

            "image":
            "https://images.unsplash.com/photo-1516280440614-37939bbacd81",

            "title":
            "Creative Intelligence",

            "theme":
            "Passion and artistic growth"

        },



        "education":{

            "image":
            "https://images.unsplash.com/photo-1523050854058-8df90110c9f1",

            "title":
            "Education Intelligence",

            "theme":
            "Learning and research"

        }

    }



    return visuals.get(

        main,

        {

        "image":

        "https://images.unsplash.com/photo-1556761175-b413da4baf72",

        "title":

        "AI Decision Intelligence",

        "theme":

        "Multi-factor decision analysis"

        }

    )
    # ============================================================
# FINAL DECISION GENERATOR
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



    score_a, score_b = calculate_scores(

        option_a,

        option_b,

        goals

    )



    if score_a >= score_b:

        winner = option_a

        alternative = option_b

    else:

        winner = option_b

        alternative = option_a




    confidence = 70


    if evidence:

        confidence += 10


    if abs(score_a-score_b) >= 10:

        confidence += 10



    confidence = min(

        confidence,

        95

    )




    return {


        # =====================================
        # INTELLIGENCE SUMMARY
        # =====================================


        "decision_intelligence":{


            "question":

            question,


            "domain":

            domain,


            "detected_goals":

            goals

        },





        # =====================================
        # RECOMMENDATION
        # =====================================


        "recommendation":{


            "choice":

            winner,


            "confidence":

            confidence,


            "reason":

            f"{winner} better matches your goals: "
            f"{', '.join(goals)}."

        },





        # =====================================
        # VISUALS
        # =====================================


        "visual_context":

        generate_visual_context(

            domain

        ),




        # =====================================
        # CHART DATA
        # =====================================


        "decision_matrix":

        build_matrix(

            option_a,

            option_b

        ),





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





        # =====================================
        # REASONING
        # =====================================


        "why":[


            f"{winner} aligns better with your detected objectives.",


            f"It provides stronger potential for "
            f"{', '.join(goals)}.",


            "The recommendation considers future value, "
            "risk and opportunity."

        ],





        "why_not":[


            f"{alternative} is still a possible choice.",


            "It may become stronger if your priorities change.",


            "The current recommendation reflects your "
            "present goals."

        ],





        "advantages":[


            f"{winner}: stronger alignment with your objectives.",


            f"{alternative}: offers different benefits."

        ],





        "disadvantages":[


            f"{winner}: requires dedication and skill development.",


            f"{alternative}: may have different growth speed."

        ],






        # =====================================
        # FUTURE SIMULATION
        # =====================================



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


            option_a:

            score_a,


            option_b:

            score_b

        },




        "evidence_count":

        len(evidence)

    }







# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================



def analyze_decision(question):


    option_a, option_b = extract_options(

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


        "status":

        "online",



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
    
