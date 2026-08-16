# ============================================================
# DECISIONLENS AI
# UNIVERSAL DECISION INTELLIGENCE ENGINE
# COMPLETE REBUILD
# PART 1/5
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
        ) as file:


            data=json.load(file)



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
            "Knowledge error:",
            e
        )



    return []




KB = load_knowledge()





# ============================================================
# TEXT INTELLIGENCE
# ============================================================



STOPWORDS={


"the",
"a",
"an",
"and",
"or",
"to",
"of",
"in",
"for",
"with",
"should",
"would",
"could",
"which",
"what",
"is",
"are",
"my",
"i",
"me",
"between",
"better",
"best",
"choose"


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


                "text":text,

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


        r"should i\s+(.+?)\s+or\s+(.+)",


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



            if len(a)>1 and len(b)>1:


                return a,b




    return None,None






# ============================================================
# DECISION TYPE UNDERSTANDING
# ============================================================



def detect_decision_type(question):


    text=normalize(question)



    categories={



        "health":[


            "eat",
            "food",
            "sleep",
            "exercise",
            "diet",
            "health",
            "rest",
            "workout"


        ],




        "career":[


            "job",
            "career",
            "salary",
            "profession",
            "ml",
            "machine learning",
            "data science",
            "developer"


        ],





        "education":[


            "study",
            "degree",
            "course",
            "phd",
            "college",
            "research"


        ],





        "travel":[


            "travel",
            "visit",
            "country",
            "trip",
            "vacation"


        ],




        "finance":[


            "money",
            "investment",
            "business",
            "buy",
            "stock"


        ],





        "relationship":[


            "friend",
            "love",
            "relationship",
            "marriage"


        ]



    }





    for category,words in categories.items():


        for word in words:


            if word in text:


                return category





    return "general"
    # ============================================================
# PART 2/5
# INTELLIGENCE LAYER
# ============================================================





# ============================================================
# USER GOAL DETECTION
# ============================================================



def detect_goals(question):


    text=normalize(question)


    goals=[]



    mapping={


        "growth":[

            "growth",
            "future",
            "career",
            "opportunity",
            "long term",
            "success"

        ],



        "money":[

            "salary",
            "money",
            "income",
            "earning",
            "pay"

        ],



        "learning":[

            "learn",
            "skill",
            "knowledge",
            "improve",
            "study"

        ],



        "health":[

            "health",
            "energy",
            "fitness",
            "sleep",
            "food",
            "diet"

        ],



        "experience":[

            "experience",
            "fun",
            "travel",
            "explore"

        ],



        "safety":[

            "safe",
            "security",
            "risk"

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
# DECISION FACTORS
# ============================================================



def get_decision_factors(decision_type):


    factors={


        "health":[

            "energy",
            "nutrition",
            "recovery",
            "wellbeing"

        ],



        "career":[

            "salary",
            "growth",
            "learning",
            "opportunity",
            "future"

        ],



        "education":[

            "knowledge",
            "research",
            "career impact",
            "difficulty"

        ],



        "travel":[

            "cost",
            "safety",
            "experience",
            "comfort"

        ],



        "finance":[

            "return",
            "risk",
            "stability",
            "growth"

        ],



        "relationship":[

            "trust",
            "compatibility",
            "happiness"

        ],



        "general":[

            "benefit",
            "risk",
            "future value"

        ]



    }



    return factors.get(

        decision_type,

        factors["general"]

    )









# ============================================================
# OPTION PROFILE ENGINE
# ============================================================



def create_option_profile(option,decision_type):


    text=normalize(option)



    profile={


        "growth":50,

        "salary":50,

        "learning":50,

        "risk":50,

        "stability":50,

        "experience":50,

        "health":50,

        "comfort":50


    }





# ------------------------------------------------------------
# CAREER
# ------------------------------------------------------------



    if decision_type=="career":



        if any(x in text for x in [

            "machine learning",

            "ml",

            "ai"

        ]):


            profile.update({


                "growth":95,

                "salary":90,

                "learning":95,

                "risk":60


            })




        elif "data science" in text:


            profile.update({


                "growth":85,

                "salary":85,

                "learning":90,

                "stability":85


            })




        elif "software" in text:


            profile.update({


                "growth":85,

                "salary":85,

                "stability":90


            })






# ------------------------------------------------------------
# HEALTH
# ------------------------------------------------------------



    if decision_type=="health":



        if "eat" in text or "food" in text:


            profile.update({


                "health":85,

                "energy":80,

                "comfort":70


            })




        if "sleep" in text:


            profile.update({


                "health":90,

                "recovery":95,

                "comfort":90


            })







# ------------------------------------------------------------
# TRAVEL
# ------------------------------------------------------------



    if decision_type=="travel":


        profile.update({


            "experience":80,

            "comfort":70,

            "risk":40


        })





# ------------------------------------------------------------
# FINANCE
# ------------------------------------------------------------



    if decision_type=="finance":


        profile.update({


            "growth":80,

            "risk":50,

            "stability":70


        })




    return profile







# ============================================================
# DECISION MATRIX BUILDER
# ============================================================



def build_matrix(

        option_a,

        option_b,

        decision_type

):


    profile_a=create_option_profile(

        option_a,

        decision_type

    )



    profile_b=create_option_profile(

        option_b,

        decision_type

    )




    factors=get_decision_factors(

        decision_type

    )




    values_a=[]

    values_b=[]





    for factor in factors:


        values_a.append(

            profile_a.get(

                factor,

                50

            )

        )


        values_b.append(

            profile_b.get(

                factor,

                50

            )

        )




    return {


        "labels":factors,


        option_a:values_a,


        option_b:values_b


    }
    # ============================================================
# PART 3/5
# DECISION REASONING ENGINE
# ============================================================





# ============================================================
# OPTION SCORING ENGINE
# ============================================================



def calculate_scores(

        option_a,

        option_b,

        decision_type,

        goals

):


    profile_a=create_option_profile(

        option_a,

        decision_type

    )


    profile_b=create_option_profile(

        option_b,

        decision_type

    )



    factors=get_decision_factors(

        decision_type

    )



    score_a=0

    score_b=0



    for factor in factors:


        score_a += profile_a.get(

            factor,

            50

        )


        score_b += profile_b.get(

            factor,

            50

        )




    score_a = score_a / len(factors)

    score_b = score_b / len(factors)





    # Goal adjustment


    for goal in goals:


        if goal=="growth":


            score_a += profile_a.get(

                "growth",

                50

            ) * 0.1


            score_b += profile_b.get(

                "growth",

                50

            ) * 0.1




        if goal=="money":


            score_a += profile_a.get(

                "salary",

                50

            ) * 0.1


            score_b += profile_b.get(

                "salary",

                50

            ) * 0.1






        if goal=="health":


            score_a += profile_a.get(

                "health",

                50

            ) * 0.1


            score_b += profile_b.get(

                "health",

                50

            ) * 0.1





    return round(score_a), round(score_b)









# ============================================================
# CONFIDENCE ENGINE
# ============================================================



def calculate_confidence(

        score_a,

        score_b,

        evidence

):


    difference=abs(

        score_a-score_b

    )



    confidence=60



    if difference>=5:

        confidence+=10



    if difference>=15:

        confidence+=10



    if evidence:

        confidence+=10




    return min(

        confidence,

        95

    )









# ============================================================
# SMART REASONING
# ============================================================



def generate_reasoning(

        winner,

        alternative,

        decision_type,

        question

):


    if decision_type=="health":


        return {


            "why":[


                f"{winner} is recommended based on health-related factors.",


                "The decision depends on your energy level, physical condition and immediate need.",


                "Health choices should prioritize wellbeing over productivity."

            ],



            "why_not":[


                f"{alternative} may also be correct depending on your situation.",


                "Additional context like timing and body condition can change the recommendation."

            ]



        }






    if decision_type=="travel":


        return {


            "why":[


                f"{winner} provides stronger overall travel value.",


                "The analysis considers safety, experience and convenience."

            ],



            "why_not":[


                f"{alternative} remains a valid travel option.",


                "The better choice depends on personal priorities."

            ]



        }






    return {


        "why":[


            f"{winner} aligns better with your detected objectives.",


            "The decision considers opportunity, future value and practical outcomes.",


            "The recommendation is based on your current priorities."

        ],



        "why_not":[


            f"{alternative} is still a possible choice.",


            "It may become better if your priorities change."

        ]



    }











# ============================================================
# FUTURE SIMULATION
# ============================================================



def generate_future_path(option,decision_type):


    text=normalize(option)



    if decision_type=="career":


        return [


            "0-1 year: Build foundational skills and projects",


            "1-3 years: Gain professional experience",


            "3-5 years: Advanced career opportunities"


        ]





    if decision_type=="health":


        return [


            "Immediate: Improve daily condition",


            "Weeks: Build healthy routine",


            "Long term: Better physical wellbeing"


        ]





    if decision_type=="travel":


        return [


            "Planning stage: Budget and preparation",


            "Experience stage: Explore and learn",


            "Long term: Memories and perspective"


        ]






    return [


        "Short term: Understand consequences",


        "Medium term: Adapt based on results",


        "Long term: Evaluate growth"


    ]









# ============================================================
# RISK REWARD SIMULATION
# ============================================================



def generate_risk_reward(

        option,

        decision_type

):


    profile=create_option_profile(

        option,

        decision_type

    )



    risk = 100 - profile.get(

        "stability",

        50

    )



    reward = (

        profile.get(

            "growth",

            50

        )

        +

        profile.get(

            "experience",

            50

        )

    ) / 2




    return {


        "risk":round(risk),


        "reward":round(reward)


    }








# ============================================================
# LOW CONFIDENCE HANDLER
# ============================================================



def needs_more_context(

        option_a,

        option_b,

        decision_type,

        score_a,

        score_b

):


    if abs(score_a-score_b)<3:


        return True



    if decision_type=="health":


        if (

            option_a in ["eat","sleep"]

            or

            option_b in ["eat","sleep"]

        ):


            return True



    return False
    # ============================================================
# PART 4/5
# FINAL DECISION PIPELINE + API
# ============================================================





# ============================================================
# COMPLETE ANALYSIS GENERATOR
# ============================================================



def generate_analysis(question):


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




    decision_type = detect_decision_type(

        question

    )




    goals = detect_goals(

        question

    )




    score_a, score_b = calculate_scores(

        option_a,

        option_b,

        decision_type,

        goals

    )





    # Winner selection


    if score_a > score_b:


        winner = option_a

        alternative = option_b



    elif score_b > score_a:


        winner = option_b

        alternative = option_a



    else:


        winner = "Need More Context"

        alternative = ""







    confidence = calculate_confidence(

        score_a,

        score_b,

        evidence

    )





    context_needed = needs_more_context(

        option_a,

        option_b,

        decision_type,

        score_a,

        score_b

    )






    reasoning = generate_reasoning(

        winner,

        alternative,

        decision_type,

        question

    )







    return {




        # -----------------------------
        # INTELLIGENCE
        # -----------------------------


        "decision_intelligence":{


            "question":question,


            "decision_type":decision_type,


            "domain":[decision_type],


            "detected_goals":goals,


            "factors":

            get_decision_factors(

                decision_type

            )

        },







        # -----------------------------
        # RECOMMENDATION
        # -----------------------------


        "recommendation":{


            "choice":winner,


            "confidence":confidence,



            "reason":(

                f"{winner} is the current recommendation "
                f"based on {decision_type} factors."

            )

        },







        # -----------------------------
        # SCORES
        # -----------------------------


        "scores":{


            option_a:score_a,


            option_b:score_b

        },







        "options":[

            option_a,

            option_b

        ],






        # -----------------------------
        # MATRIX DATA
        # -----------------------------


        "decision_matrix":

        build_matrix(

            option_a,

            option_b,

            decision_type

        ),







        # -----------------------------
        # REASONING
        # -----------------------------


        "why":

        reasoning["why"],




        "why_not":

        reasoning["why_not"],







        "advantages":[


            f"{option_a}: evaluated using {decision_type} intelligence.",


            f"{option_b}: evaluated using {decision_type} intelligence."

        ],







        "disadvantages":[


            "Every choice has trade-offs.",


            "The final decision depends on personal circumstances."

        ],








        # -----------------------------
        # SIMULATION
        # -----------------------------



        "risk_reward":{


            option_a:

            generate_risk_reward(

                option_a,

                decision_type

            ),




            option_b:

            generate_risk_reward(

                option_b,

                decision_type

            )

        },







        "future_paths":{


            option_a:

            generate_future_path(

                option_a,

                decision_type

            ),



            option_b:

            generate_future_path(

                option_b,

                decision_type

            )


        },







        "timeline":{


            winner:

            generate_future_path(

                winner,

                decision_type

            )


        },







        "needs_context":

        context_needed,





        "evidence_count":

        len(evidence)





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


        "engine":

        "DecisionLens Intelligence Engine",



        "knowledge_records":

        len(KB)


    })









# ============================================================
# MAIN ANALYSIS API
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





        if len(question)<5:


            return jsonify({


                "error":

                "Please enter a decision"

            }),400





        result = generate_analysis(

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
# PART 5/5
# SERVER STARTUP
# DEPLOYMENT READY
# ============================================================





# ============================================================
# ERROR HANDLERS
# ============================================================


@app.errorhandler(404)
def page_not_found(error):


    return jsonify({


        "error":

        "Route not found"



    }),404






@app.errorhandler(500)
def server_error(error):


    return jsonify({


        "error":

        "Internal server error"



    }),500







# ============================================================
# DEPLOYMENT ENTRY POINT
# ============================================================



if __name__ == "__main__":


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
