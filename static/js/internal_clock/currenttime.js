function userTime() {
    let date = new Date();

    let hours = date.getHours();
    let minutes = date.getMinutes();
    let seconds = date.getSeconds();

   hours = (hours < 10) ? "0" + hours : hours;
   minutes = (minutes < 10) ? "0" + minutes : minutes;
   seconds = (seconds < 10) ? "0" + seconds : seconds;

   try{
       document.getElementById("clock").innerText = hours + ":" + minutes + ":" + seconds;
       setTimeout(function(){ userTime() }, 1000);
   } catch (TypeError){
        // do nothing
   }
}

userTime();



// window.addEventListener('load', function (evt ){
//     console.log("running this window event usertime ")
//     console.log(evt.target.id)
//
//     userTime();
//     manipulateClockInDateDisplay();
// }, {once: true})
//
//
document.getElementById('user-content').addEventListener('htmx:afterRequest', function(evt){
    if(document.getElementById("clock-ins")){
         userTime();
        manipulateClockInDateDisplay();
    }
})
