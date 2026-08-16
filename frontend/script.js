// ============================================================
// DECISIONLENS AI
// STABLE REPORT ENGINE
// ============================================================


const result = JSON.parse(
    localStorage.getItem("decisionResult")
);



console.log(
    "DECISION RESULT:",
    result
);





if(!result){


document.body.innerHTML = `

<h1 style="text-align:center;margin-top:100px">

No decision data found

</h1>

`;


}

else{



// ============================================================
// SAFE VALUE FUNCTION
// ============================================================


function safe(value){


if(value===undefined || value===null){

return "--";

}


if(Array.isArray(value)){

return value.join(", ");

}


return value;


}






// ============================================================
// BASIC INFORMATION
// ============================================================



const intelligence =
result.decision_intelligence || {};



document.getElementById("question").innerHTML =
safe(
intelligence.question || result.decision
);



document.getElementById("domain").innerHTML =
safe(
intelligence.domain
);



document.getElementById("goals").innerHTML =
safe(
intelligence.detected_goals
);







// ============================================================
// VISUAL CONTEXT
// ============================================================



if(result.visual_context){


document.getElementById(
"domainImage"
).src =
result.visual_context.image;


document.getElementById(
"visualText"
).innerHTML =
safe(
result.visual_context.theme
);


}








// ============================================================
// RECOMMENDATION
// ============================================================



const recommendation =
result.recommendation || {};



document.getElementById(
"recommendation"
).innerHTML =
safe(
recommendation.choice
);



document.getElementById(
"reason"
).innerHTML =
safe(
recommendation.reason
);



document.getElementById(
"confidence"
).innerHTML =
safe(
recommendation.confidence
)
+
"%";








// ============================================================
// SCORE CARDS
// ============================================================


const scoreBox =
document.getElementById(
"scores"
);



scoreBox.innerHTML="";



Object.entries(
result.scores || {}
)
.forEach(([name,score])=>{


scoreBox.innerHTML += `


<div class="score-card">


<h3>
${name}
</h3>


<div class="score-number">

${score}

</div>


<p>
AI Compatibility
</p>


</div>


`;


});









// ============================================================
// LIST CREATOR
// ============================================================


function createList(
id,
data
){


const box =
document.getElementById(id);



box.innerHTML="";



if(!data)
return;



if(!Array.isArray(data)){

data=[data];

}



data.forEach(item=>{


let li=document.createElement(
"li"
);



li.innerHTML=item;


box.appendChild(li);



});



}



createList(
"why",
result.why
);



createList(
"whyNot",
result.why_not
);



createList(
"advantages",
result.advantages
);



createList(
"disadvantages",
result.disadvantages
);









// ============================================================
// RADAR CHART
// ============================================================



const matrix =
result.decision_matrix;



if(matrix){



new Chart(

document.getElementById(
"radarChart"
),

{


type:"radar",


data:{


labels:
matrix.labels || matrix.factors || [],



datasets:[


{

label:
result.options?.[0] || "Option 1",


data:
matrix[
result.options?.[0]
] || [],


borderWidth:2

},



{

label:
result.options?.[1] || "Option 2",


data:
matrix[
result.options?.[1]
] || [],


borderWidth:2

}


]

},



options:{


responsive:true,


scales:{


r:{


beginAtZero:true,

max:100


}


}



}



}

);



}









// ============================================================
// RISK REWARD CHART
// ============================================================


const risk =
result.risk_reward;



if(risk){


let names =
Object.keys(risk);



new Chart(

document.getElementById(
"riskChart"
),


{


type:"bar",


data:{


labels:names,


datasets:[


{


label:"Risk",


data:names.map(
x=>risk[x].risk
)


},



{


label:"Reward",


data:names.map(
x=>risk[x].reward
)


}



]


},


options:{


responsive:true,


scales:{


y:{


beginAtZero:true,

max:100


}


}


}



}



);



}









// ============================================================
// FUTURE PATH
// ============================================================


const futureBox =
document.getElementById(
"futurePath"
);



futureBox.innerHTML="";



Object.entries(
result.future_paths || {}
)
.forEach(
([name,path])=>{


let content="";



if(Array.isArray(path)){


content =
path.map(
x=>`<li>${x}</li>`
)
.join("");

}

else{


content =
`<li>${path}</li>`;

}



futureBox.innerHTML += `


<div class="timeline-item">


<h3>
${name}
</h3>


<ul>

${content}

</ul>


</div>


`;



}

);








// ============================================================
// TIMELINE
// ============================================================



const timelineBox =
document.getElementById(
"timeline"
);



timelineBox.innerHTML="";



const timelineData =
Object.values(
result.timeline || {}
)[0];



if(timelineData){


if(Array.isArray(timelineData)){


timelineData.forEach(step=>{


timelineBox.innerHTML += `


<div class="timeline-item">

${step}

</div>


`;


});


}

else{


timelineBox.innerHTML = `

<div class="timeline-item">

${timelineData}

</div>

`;

}


}



}
