# ============================================================
# DECISIONLENS AI
# AI DECISION INTELLIGENCE PLATFORM
# ADVANCED OR-DECISION ENGINE
#
# APP.PY PART 1/5
# FRONTEND COMPATIBLE VERSION
# ============================================================


from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

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

        print(
            "Knowledge base not found"
        )

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

                "knowledge",
                "documents",
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


    words=re.findall(

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


        output=[]


        for key in [

            "title",
            "topic",
            "content",
            "text",
            "summary",
            "description"

        ]:


            if item.get(key):

                output.append(

                    str(item[key])

                )



        return " ".join(output)




    return str(item)








# ============================================================
# QUERY INTELLIGENCE ENGINE
# ============================================================



def understand_query(question):


    text=normalize(question)



    intelligence={


        "domain":[],

        "goals":[],

        "decision_type":"comparison"

    }







    # -----------------------------
    # DOMAIN DETECTION
    # -----------------------------


    domains={



        "technology":[


            "ai",
            "ml",
            "machine learning",
            "data science",
            "python",
            "coding",
            "software",
            "robotics",
            "cybersecurity"

        ],




        "career":[


            "job",
            "career",
            "salary",
            "profession",
            "role"

        ],




        "education":[


            "phd",
            "degree",
            "college",
            "study",
            "research",
            "course"

        ],




        "finance":[


            "money",
            "investment",
            "business",
            "startup"

        ],




        "creative":[


            "dance",
            "sing",
            "music",
            "art",
            "design"

        ]



    }







    for domain,words in domains.items():


        for word in words:


            if word in text:


                intelligence["domain"].append(

                    domain

                )

                break






    if not intelligence["domain"]:


        intelligence["domain"]=[

            "general"

        ]









    # -----------------------------
    # GOAL DETECTION
    # -----------------------------


    goals={



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
            "scope",
            "career",
            "opportunity"

        ],




        "learning":[

            "learn",
            "skill",
            "knowledge",
            "improve"

        ],




        "research":[

            "research",
            "innovation",
            "paper"

        ],




        "passion":[

            "love",
            "passion",
            "interest",
            "enjoy"

        ],




        "stability":[

            "stable",
            "safe",
            "security"

        ]



    }








    for goal,words in goals.items():


        for word in words:


            if word in text:


                intelligence["goals"].append(

                    goal

                )

                break







    if not intelligence["goals"]:


        intelligence["goals"]=[

            "growth",
            "future"

        ]








    # -----------------------------
    # DECISION TYPE
    # -----------------------------


    if any(x in text for x in [

        "buy",
        "purchase",
        "invest"

    ]):


        intelligence["decision_type"]="financial"




    elif any(x in text for x in [

        "learn",
        "become",
        "roadmap"

    ]):


        intelligence["decision_type"]="guidance"




    return intelligence
    # ============================================================
# PART 2/5
# OPTION UNDERSTANDING + RAG INTELLIGENCE
# ============================================================




# ============================================================
# OPTION EXTRACTION ENGINE
# ============================================================


def clean_option(text):


    text=text.strip(
        " ?.,:"
    )



    remove_words=[


        "should i",

        "should we",

        "which is better",

        "what is better",

        "choose",

        "select",

        "pick"

    ]



    for word in remove_words:


        text=re.sub(

            word,

            "",

            text,

            flags=re.I

        )



    return text.strip()







def extract_options(question):


    patterns=[



        # Python vs Java


        r"(.+?)\s+vs\.?\s+(.+)",




        # between A and B


        r"between\s+(.+?)\s+and\s+(.+)",




        # should I A or B


        r"should i\s+(.+?)\s+or\s+(.+)",




        # A or B


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
# ADVANCED RAG RETRIEVAL
# ============================================================



def retrieve_evidence(question):


    query_tokens=set(

        tokenize(question)

    )



    results=[]





    for item in KB:



        text=extract_text(item)



        item_tokens=set(

            tokenize(text)

        )



        common=query_tokens.intersection(

            item_tokens

        )



        score=len(common)





        # bonus for exact phrases


        for token in query_tokens:


            if token in normalize(text):


                score += 2





        if score>0:


            results.append({


                "content":text,


                "score":score


            })






    results.sort(

        key=lambda x:x["score"],

        reverse=True

    )




    return results[:8]









# ============================================================
# OPTION PROFILE DATABASE
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







    # ========================================================
    # TECHNOLOGY OPTIONS
    # ========================================================


    if any(x in text for x in [

        "machine learning",

        "ml",

        "deep learning",

        "ai"

    ]):


        profile.update({


            "salary":90,

            "growth":95,

            "learning":95,

            "research":90,

            "stability":80,

            "difficulty":85,

            "risk":60


        })






    elif "data science" in text:


        profile.update({


            "salary":88,

            "growth":88,

            "learning":85,

            "research":70,

            "stability":90,

            "difficulty":70,

            "risk":45


        })







    elif "software" in text or "developer" in text:


        profile.update({


            "salary":85,

            "growth":85,

            "learning":80,

            "stability":90,

            "difficulty":75


        })







    elif "python" in text:


        profile.update({


            "learning":90,

            "growth":85


        })








    # ========================================================
    # EDUCATION OPTIONS
    # ========================================================


    if "phd" in text or "research" in text:


        profile.update({


            "research":95,

            "learning":95,

            "salary":65,

            "difficulty":90,

            "risk":70


        })








    # ========================================================
    # CREATIVE OPTIONS
    # ========================================================


    if any(x in text for x in [

        "dance",

        "music",

        "sing",

        "art"

    ]):


        profile.update({


            "creativity":95,

            "growth":75,

            "passion":95,

            "risk":65


        })






    # ========================================================
    # BUSINESS OPTIONS
    # ========================================================


    if "startup" in text or "business" in text:


        profile.update({


            "growth":95,

            "salary":90,

            "risk":90,

            "stability":40


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

            profile_a.get(

                factor,

                50

            )

            for factor in factors

        ],




        option_b:[

            profile_b.get(

                factor,

                50

            )

            for factor in factors

        ]


    }
    # ============================================================
# PART 3/5
# DECISION SCORING + SIMULATION ENGINE
# ============================================================





# ============================================================
# GOAL WEIGHTING ENGINE
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




    score_a = score_a / len(goals)

    score_b = score_b / len(goals)



    return (

        round(score_a),

        round(score_b)

    )








# ============================================================
# RISK REWARD SIMULATION
# ============================================================



def generate_risk_reward(option):


    profile=create_option_profile(

        option

    )



    risk = profile.get(

        "risk",

        50

    )



    reward = (

        profile.get(

            "growth",

            50

        )

        +

        profile.get(

            "salary",

            50

        )

        +

        profile.get(

            "learning",

            50

        )

    ) // 3




    return {


        "risk":risk,


        "reward":reward,


        "success_probability":

        max(

            40,

            100-risk+reward//2

        )


    }








# ============================================================
# FUTURE PATH GENERATOR
# ============================================================



def generate_future_path(option):


    text=normalize(option)



    if "machine" in text or "ml" in text:


        return [


            "AI Engineer",


            "Machine Learning Engineer",


            "Deep Learning Specialist",


            "Research Engineer"



        ]





    if "data science" in text:


        return [


            "Data Analyst",


            "Data Scientist",


            "ML Data Scientist",


            "Analytics Lead"



        ]






    if "software" in text or "developer" in text:


        return [


            "Software Developer",


            "Backend Engineer",


            "Senior Software Engineer",


            "Engineering Lead"


        ]






    if "phd" in text or "research" in text:


        return [


            "Research Student",


            "Research Associate",


            "Scientist",


            "Research Leader"


        ]






    return [


        "Foundation Building",


        "Skill Development",


        "Professional Growth"


    ]










# ============================================================
# TIMELINE SIMULATOR
# ============================================================



def generate_timeline(option):


    text=normalize(option)





    if "machine" in text or "ml" in text:


        return [


            "0-6 months: Learn ML algorithms, Python and mathematics",


            "6-18 months: Build AI projects and practical systems",


            "2-3 years: Become ML/AI Engineer",


            "5+ years: Senior AI Engineer or Research Scientist"



        ]







    if "data science" in text:


        return [


            "0-6 months: Statistics, SQL and analytics",


            "6-18 months: Build data science portfolio",


            "2-3 years: Data Scientist role",


            "5+ years: Analytics Lead"



        ]







    return [


        "Short term: Build skills",


        "Medium term: Gain experience",


        "Long term: Professional growth"


    ]









# ============================================================
# FINAL DECISION ENGINE
# ============================================================



def generate_analysis(
        option_a,
        option_b,
        question,
        evidence
):


    intelligence = understand_query(

        question

    )



    goals=intelligence[

        "goals"

    ]





    score_a,score_b = calculate_scores(

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





    confidence=min(

        confidence,

        95

    )






    return {


        # ==========================
        # INTELLIGENCE
        # ==========================


        "decision_intelligence":{


            "question":question,


            "domain":

            intelligence["domain"],


            "detected_goals":

            goals


        },




        # ==========================
        # RECOMMENDATION
        # ==========================


        "recommendation":{


            "choice":winner,


            "confidence":confidence,


            "reason":

            f"{winner} better matches your goals of {', '.join(goals)}."

        },






        # ==========================
        # SCORES
        # ==========================


        "scores":{


            option_a:score_a,


            option_b:score_b


        },





        # ==========================
        # MATRIX
        # ==========================


        "decision_matrix":

        build_matrix(

            option_a,

            option_b

        ),





        # ==========================
        # EXPLANATION
        # ==========================


        "why":[


            f"{winner} aligns better with your detected priorities.",


            f"It provides stronger potential for {', '.join(goals)}.",


            "The recommendation considers future opportunities and trade-offs."

        ],





        "why_not":[


            f"{alternative} is still a possible choice.",


            "It may become better if your priorities change.",


            "Current recommendation is based on your present goals."

        ],






        "advantages":[


            f"{winner}: stronger alignment with your objectives.",


            f"{alternative}: offers different benefits."

        ],






        "disadvantages":[


            f"{winner}: requires commitment and continuous learning.",


            f"{alternative}: may have slower alignment with your goals."

        ],






        # ==========================
        # SIMULATION
        # ==========================


        "risk_reward":{


            option_a:

            generate_risk_reward(option_a),


            option_b:

            generate_risk_reward(option_b)


        },





        "future_paths":{


            option_a:

            generate_future_path(option_a),


            option_b:

            generate_future_path(option_b)


        },





        "timeline":{


            winner:

            generate_timeline(winner)


        },





        "evidence_count":

        len(evidence)


    }
    # ============================================================
# PART 4/5
# MAIN ANALYZER + API ROUTES
# ============================================================






# ============================================================
# MAIN DECISION ANALYZER
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

def result_page():


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


        "status":

        "online",



        "engine":

        "DecisionLens AI Intelligence Engine",




        "knowledge_records":

        len(KB)


    })









# ============================================================
# MAIN AI API
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







        result = analyze_decision(

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

            "Decision engine failed",



            "details":

            str(e)



        }),500
        # ============================================================
# PART 5/5
# VISUAL INTELLIGENCE + SERVER START
# ============================================================






# ============================================================
# VISUAL CONTEXT GENERATOR
# ============================================================


def generate_visual_context(domain):


    visuals={


        "technology":{


            "image":

            "https://images.unsplash.com/photo-1518770660439-4636190af475",


            "theme":

            "Artificial Intelligence & Technology",


            "title":

            "Technology Decision Intelligence"


        },



        "career":{


            "image":

            "https://images.unsplash.com/photo-1521737711867-e3b97375f902",


            "theme":

            "Career Growth Simulation",


            "title":

            "Professional Path Analysis"


        },



        "education":{


            "image":

            "https://images.unsplash.com/photo-1523240795612-9a054b0db644",


            "theme":

            "Learning & Research",


            "title":

            "Education Decision Analysis"


        },



        "finance":{


            "image":

            "https://images.unsplash.com/photo-1559526324-593bc073d938",


            "theme":

            "Financial Intelligence",


            "title":

            "Risk Reward Simulation"


        },



        "creative":{


            "image":

            "https://images.unsplash.com/photo-1513364776144-60967b0f800f",


            "theme":

            "Creative Intelligence",


            "title":

            "Passion Based Decision"


        }


    }





    if domain in visuals:


        return visuals[domain]



    return {


        "image":

        "https://images.unsplash.com/photo-1551288049-bebda4e38f71",


        "theme":

        "AI Decision Intelligence",


        "title":

        "Universal Decision Analysis"


    }









# ============================================================
# ADD VISUAL CONTEXT TO RESPONSE
# ============================================================


def attach_visuals(result):


    try:


        domain = result[

            "decision_intelligence"

        ][

            "domain"

        ][0]




        result["visual_context"] = generate_visual_context(

            domain

        )



    except Exception:



        result["visual_context"]={


            "title":

            "Decision Intelligence",


            "theme":

            "AI Analysis"



        }



    return result







# ============================================================
# OVERRIDE ANALYSIS WITH VISUAL LAYER
# ============================================================


old_analyze_decision = analyze_decision



def enhanced_analyze_decision(question):


    result = old_analyze_decision(

        question

    )


    if "error" not in result:


        result = attach_visuals(

            result

        )



    return result




analyze_decision = enhanced_analyze_decision







# ============================================================
# APPLICATION START
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
