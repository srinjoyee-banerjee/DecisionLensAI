// ============================================================
// DECISIONLENS AI
// FRONTEND DECISION ANALYZER ENGINE
// ============================================================



const analyzeBtn = document.getElementById(
    "analyzeBtn"
);

const decisionInput = document.getElementById(
    "decisionInput"
);

const btnText = document.getElementById(
    "btnText"
);

const errorBox = document.getElementById(
    "errorBox"
);




// ============================================================
// DASHBOARD PAGE
// ============================================================


if(analyzeBtn){


analyzeBtn.addEventListener(
"click",
async function(){


const decision =
decisionInput.value.trim();



if(!decision){


errorBox.innerHTML =
"Please describe your decision first.";


return;


}




btnText.innerHTML =
"ANALYZING...";


analyzeBtn.disabled=true;


errorBox.innerHTML="";



try{


const response =
await fetch(
"/api/analyze",
{

method:"POST",

headers:
{

"Content-Type":
"application/json"

},


body:
JSON.stringify(
{

decision:decision

}

)

}

);




const data =
await response.json();





if(!response.ok ||
data.error){


throw new Error(
data.error ||
"Analysis failed"
);


}




// save complete AI report

localStorage.setItem(

"decisionResult",

JSON.stringify(data)

);




// redirect

window.location.href =
"result.html";



}

catch(error){


console.error(
"DecisionLens Error:",
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







// ============================================================
// RESULT PAGE ENGINE
// ============================================================



function loadDecisionResult(){



const result =
localStorage.getItem(
"decisionResult"
);



if(!result){

return;

}



const data =
JSON.parse(result);





// Main decision


const decisionText =
document.getElementById(
"decisionText"
);


if(decisionText){

decisionText.innerHTML =
data.decision_intelligence ||
data.decision ||
"Decision Analysis";

}




// Recommendation


const recommendation =
document.getElementById(
"recommendation"
);


if(recommendation){

recommendation.innerHTML =
data.recommendation ||
"--";

}





// Confidence


const confidence =
document.getElementById(
"confidence"
);


if(confidence){

confidence.innerHTML =
(data.confidence || 0)
+
"%";

}





// Summary


const summary =
document.getElementById(
"summary"
);


if(summary){

summary.innerHTML =
data.primary_reason ||
data.summary ||
"";

}





renderList(
"why",
data.why
);


renderList(
"whyNot",
data.why_not
);


renderList(
"advantages",
data.advantages
);


renderList(
"disadvantages",
data.disadvantages
);


renderList(
"tradeoffs",
data.tradeoffs
);



}





function renderList(
elementId,
items
){



const box =
document.getElementById(
elementId
);



if(!box){

return;

}



box.innerHTML="";



if(!items ||
items.length===0){

box.innerHTML =
"<li>No information available</li>";

return;

}




items.forEach(
(item)=>{


const li =
document.createElement(
"li"
);


li.innerText=item;


box.appendChild(li);



}

);


}





// Run only on result page

if(
window.location.pathname.includes(
"result.html"
)
){


loadDecisionResult();


}
