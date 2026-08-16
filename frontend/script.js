// ============================================================
// DECISIONLENS AI
// FRONTEND DECISION ANALYZER
// ============================================================


const analyzeBtn = document.getElementById("analyzeBtn");
const decisionInput = document.getElementById("decisionInput");
const btnText = document.getElementById("btnText");
const errorBox = document.getElementById("errorBox");





if(analyzeBtn){


analyzeBtn.addEventListener(
"click",
async function(){


let decision = decisionInput.value.trim();



if(!decision){


errorBox.innerHTML =
"Please describe your decision first.";

return;

}



btnText.innerHTML =
"ANALYZING...";

analyzeBtn.disabled = true;



errorBox.innerHTML = "";





try{


const response = await fetch(
"/api/analyze",
{

method:"POST",

headers:
{
"Content-Type":"application/json"
},


body:
JSON.stringify(
{
decision:decision
}
)

}

);





const data = await response.json();





if(!response.ok){


throw new Error(
data.error ||
"Analysis failed"
);


}






// store result

localStorage.setItem(
"decisionResult",
JSON.stringify(data)
);




// move to result page

window.location.href =
"result.html";





}



catch(error){


console.error(
error
);



errorBox.innerHTML =
error.message;



btnText.innerHTML =
"ANALYZE DECISION";

analyzeBtn.disabled=false;


}



});


}
