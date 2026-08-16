// ============================================================
// DECISIONLENS AI
// FRONTEND CONTROLLER
// ============================================================


const API_URL = "/api/analyze";



// ============================================================
// ANALYZE DECISION
// ============================================================


async function analyzeDecision(){


    const input =
        document.getElementById(
            "decisionInput"
        );


    if(!input){

        console.error(
            "Decision input not found"
        );

        return;

    }



    const decision =
        input.value.trim();



    if(decision.length < 5){

        alert(
            "Please enter a proper decision."
        );

        return;

    }



    const button =
        document.getElementById(
            "analyzeBtn"
        );



    if(button){

        button.innerHTML =
        "ANALYZING...";

        button.disabled=true;

    }



    try{


        const response =
        await fetch(
            API_URL,
            {

                method:"POST",

                headers:{

                    "Content-Type":
                    "application/json"

                },


                body:
                JSON.stringify({

                    decision:decision

                })

            }
        );



        const data =
        await response.json();



        console.log(
            "Decision Result:",
            data
        );



        if(data.error){


            alert(
                data.error
            );


            return;

        }




        // SAVE RESULT FOR RESULT PAGE

        localStorage.setItem(

            "decisionResult",

            JSON.stringify(data)

        );



        // MOVE TO REPORT

        window.location.href =
        "/result.html";



    }



    catch(error){


        console.error(
            error
        );


        alert(
            "Unable to connect with DecisionLens AI."
        );


    }



    finally{


        if(button){

            button.innerHTML =
            "ANALYZE DECISION →";

            button.disabled=false;

        }


    }


}





// ============================================================
// PAGE LOAD
// ============================================================


document.addEventListener(
"DOMContentLoaded",
()=>{


    const button =
    document.getElementById(
        "analyzeBtn"
    );



    if(button){


        button.addEventListener(

            "click",

            analyzeDecision

        );


    }



});
