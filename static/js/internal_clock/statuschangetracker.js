// register event for when the countdown is over
let myEvent = new Event('countdownOver', {
    bubbles: true,
    cancelable: true,
    composed: false
});


const timeUntilSwap = () => {
    let serverDate =
        document.getElementById("js-status").getAttribute("clock-time");
    let countDownDate =
        new Date(serverDate);

    let now = new Date().getTime();
    let timeleft = countDownDate - now;

    // Calculating the days, hours, minutes and seconds left
    let seconds = Math.floor((timeleft % (1000 * 60)) / 1000);
    //  swap subtraction method when the current time is greater than the time used for countdown
    if ((seconds < 0)){
        timeleft = now - countDownDate;
        seconds = Math.floor((timeleft % (1000 * 60)) / 1000);
    }
    let days = Math.floor(timeleft / (1000 * 60 * 60 * 24));
    let hours = Math.floor((timeleft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    let minutes = Math.floor((timeleft % (1000 * 60 * 60)) / (1000 * 60));

    if (days >= 1) {
        let dayText = "days";
        if (days === 1){dayText = "day";}
        document.getElementById("js-status").innerHTML = days + " " + dayText;
    }
    if (days === 0 && hours >= 1){
        let hourText = "hours"
        if (hours === 1) {hourText = "hour";}
        document.getElementById("js-status").innerHTML = hours + " " + hourText;
    } else if (days === 0 && hours === 0 && minutes >= 1) {
        let minuteText = "minutes";
        if (minutes === 1) {minuteText = "minute";}
        document.getElementById("js-status").innerHTML = minutes + " " + minuteText;
    } else if (days ===0 && hours === 0 && minutes === 0 && seconds >= 0) {
        let secondText= "seconds";
        if (seconds === 1) {secondText = "second";}
        document.getElementById("js-status").innerHTML = seconds + " seconds";
    }

    if (seconds === 0 && minutes === 0 && hours === 0 && days === 0){
        document.getElementById("js-status").dispatchEvent(myEvent);
    }
    document.getElementById("user-test").innerHTML = days + " " + hours + " " + minutes + " " + seconds;

    let countdownSwap = setTimeout(function(){timeUntilSwap()}, 1000);
};

timeUntilSwap();