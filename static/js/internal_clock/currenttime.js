const userTime = ()=> {
    let date = new Date();
    let hours = date.getHours();
    let minutes = date.getMinutes();
    let seconds = date.getSeconds();

   hours = (hours < 10) ? "0" + hours : hours;
   minutes = (minutes < 10) ? "0" + minutes : minutes;
   seconds = (seconds < 10) ? "0" + seconds : seconds;

    document.getElementById("clock").innerText = hours + ":" + minutes + ":" + seconds;
    let myTime = setTimeout(function(){ userTime() }, 1000);
};
userTime();