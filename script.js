function setExample(text){

const input =
document.getElementById("decisionInput");

if(input){

input.value=text;
input.focus();

}

}


function analyzeDecision(){

const input =
document.getElementById("decisionInput");

const decision =
input.value.trim();


if(!decision){

alert("Please enter a decision.");

return;

}


sessionStorage.setItem(
"decisionQuery",
decision
);


window.location.href="/result.html";

}


async function loadResult(){

const query =
sessionStorage.getItem(
"decisionQuery"
);


const queryElement =
document.getElementById("query");


if(!queryElement || !query)
return;


queryElement.textContent=query;


try{

const response =
await fetch(
"/api/analyze",
{

method:"POST",

headers:{
"Content-Type":
"application/json"
},

body:JSON.stringify({
query:query
})

}
);


if(!response.ok){

throw new Error(
"API request failed"
);

}


const data =
await response.json();


displayResult(data);


}

catch(error){

console.error(error);

document.getElementById(
"analysis"
).textContent =
"Unable to connect to DecisionLens AI. Please try again.";

}

}


function displayResult(data){

const analysis =
data.recommendation ||
data.response ||
"";


document.getElementById(
"analysis"
).textContent =
analysis;


const tools =
data.tools_used || [];


const toolsContainer =
document.getElementById(
"tools"
);


toolsContainer.innerHTML="";


tools.forEach(tool=>{

const div =
document.createElement(
"div"
);

div.className="tool";

div.textContent =
"✓ " + tool;

toolsContainer.appendChild(
div
);

});


const evidence =
data.evidence || [];


const evidenceContainer =
document.getElementById(
"evidence"
);


evidenceContainer.innerHTML="";


evidence.forEach(item=>{

const div =
document.createElement(
"div"
);

div.className =
"evidence-item";


div.innerHTML =
"<div class='evidence-title'>" +
item.title +
"</div>" +

"<div class='similarity'>" +
"Similarity: " +
Number(item.score).toFixed(3) +
"</div>";


evidenceContainer.appendChild(
div
);

});


document.getElementById(
"recommendation"
).textContent =
extractRecommendation(
analysis
);

}


function extractRecommendation(text){

const match =
text.match(
/RECOMMENDATION[:\s]*([\s\S]*?)(?=KEY FACTORS|OPTION A|$)/i
);


if(match){

return match[1].trim();

}


return "See complete AI analysis below.";

}


if(
window.location.pathname.endsWith(
"result.html"
)
){

loadResult();

}
