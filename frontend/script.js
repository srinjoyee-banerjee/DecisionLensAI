// ============================================================
// DECISIONLENS AI
// FRONTEND INTELLIGENCE CONTROLLER
// ============================================================



const analyzeBtn =
document.getElementById(
"analyzeBtn"
);


const decisionInput =
document.getElementById(
"decisionInput"
);



const btnText =
document.getElementById(
"btnText"
);



const errorBox =
document.getElementById(
"errorBox"
);





if(analyzeBtn){



analyzeBtn.addEventListener(

"click",

async()=>{



let question =
decisionInput.value.trim();




if(question.length < 5){


errorBox.innerHTML =
"Please enter a meaningful decision.";


return;

}





btnText.innerHTML =
"AI THINKING...";



analyzeBtn.disabled=true;



errorBox.innerHTML="";







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

decision:question

})


}

);






const result =
await response.json();







if(!response.ok || result.error){


throw new Error(

result.error ||

"Analysis failed"

);


}







// SAVE AI REPORT


localStorage.setItem(

"decisionResult",

JSON.stringify(result)

);








btnText.innerHTML =
"COMPLETE";





setTimeout(()=>{


window.location.href =
"result.html";



},500);








}

catch(error){



console.error(error);



errorBox.innerHTML =

error.message;



btnText.innerHTML =
"ANALYZE DECISION";


analyzeBtn.disabled=false;



}



}


);



}
