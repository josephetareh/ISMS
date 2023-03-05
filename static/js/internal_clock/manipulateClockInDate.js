// const divmod = (x, y) => [Math.floor(x / y), x % y];
function divmod(x, y){
    return [Math.floor(x / y), x % y]
}

function years(durationInSeconds){
    let yearDivMod = divmod(durationInSeconds, 31536000);
    return {
        divmod: yearDivMod,
        plural: "Years",
        singular: "Year",
        totalTime: yearDivMod[0],
        RemainderInSeconds: yearDivMod[1]
    }
}

function days (durationInSeconds){
    let dayDivMod = divmod(durationInSeconds, 86400);
    return {
        divmod: dayDivMod,
        plural: "Days",
        singular: "Day",
        totalTime: dayDivMod[0],
        RemainderInSeconds: dayDivMod[1]
    }
}

function hours (durationInSeconds){
    let hourDivMod = divmod(durationInSeconds, 3600)
    return {
    divmod: hourDivMod,
    plural: "Hours",
    singular: "Hour",
    totalTime: hourDivMod[0],
    RemainderInSeconds: hourDivMod[1]
    }
}

function minutes(durationInSeconds){
    let minuteDivMod = divmod(durationInSeconds, 60)
    return {
        divmod: minuteDivMod,
        plural: "Minutes",
        singular: "Minute",
        totalTime: minuteDivMod[0],
        RemainderInSeconds: minuteDivMod[1]
    }
}

function seconds (durationInSeconds){
    let secondsDivMod = divmod(durationInSeconds, 1)
    return {
        divmod: secondsDivMod,
        plural: "Seconds",
        singular: "Second",
        totalTime: secondsDivMod[0],
        RemainderInSeconds: secondsDivMod[1]
    }
}

function totalDuration(durationInSeconds) {
    let totalYears = years(durationInSeconds)
    let totalDays = days(totalYears.RemainderInSeconds)
    let totalHours = hours(totalDays.RemainderInSeconds)
    let totalMinutes = minutes(totalHours.RemainderInSeconds)
    let totalSeconds = seconds(totalMinutes.RemainderInSeconds)
    return [totalYears, totalDays, totalHours, totalMinutes, totalSeconds]
}


function manipulateClockInDateDisplay(){
    const clockInTime = document.getElementById('clock-in-starts');
    const clockInIdentifier= document.getElementById('time-until-classifier');
    const clockInStatus = document.getElementById('clock-in-status');

    if (clockInTime.hasAttribute('data-next-clock-in-time-to-open')
        && clockInTime.getAttribute('data-next-clock-in-time-to-open') !== ""){

        const clock = document.getElementById('clock');
        let openingTime = new Date(clockInTime.getAttribute('data-next-clock-in-time-to-open'))
        let shiftTime = new Date(clockInTime.getAttribute('data-shift-starting-time'))
        console.log("opening time" + openingTime)
        console.log("closing time" + shiftTime)

        let hasClockInBeenActivated = (clockInTime.getAttribute('data-shift-activated'))
        let clockInActive = false
        hasClockInBeenActivated === "True" ? clockInActive = true : clockInActive = false;

        if (clockInActive === false) { // if the clock in has not been activated
            clockInStatus.innerHTML = "Clock in Opens In"
            let currentTime = new Date()
            let timeUntilOpen = openingTime - currentTime;
            console.log(timeUntilOpen)
            timeUntilOpen = timeUntilOpen / 1000;    //  converts timeUntilOpen from milliseconds to seconds
            let durationForClockInBeginning = totalDuration(timeUntilOpen)
            console.log(durationForClockInBeginning)

            // find the first instance of time that is greater than 1:
            let currentTimeStatus = durationForClockInBeginning.find(item => item.totalTime >= 1)
            console.log(currentTimeStatus)
            clockInTime.innerHTML = currentTimeStatus.totalTime
            currentTimeStatus.totalTime > 1
                ? clockInIdentifier.innerHTML = currentTimeStatus.plural : clockInIdentifier.innerHTML = currentTimeStatus.singular;
            // todo: htmx event listener to reload the page and then add a timeout function here
        } else {
            // if the clock in has been activated already:check if the user is on shift
            let currentTime = new Date();
            const clockInButton = document.getElementById('clock-in-button');

            let hasShiftBeenStarted = clockInTime.getAttribute('data-shift-started');
            let shiftStarted = false
            hasShiftBeenStarted === "True" ? shiftStarted = true : shiftStarted = false;

            if (shiftStarted === false) {
                let timeUntilClockInCloses = shiftTime - currentTime;
                clockInButton.disabled = false
                clockInStatus.innerHTML = "Clock in Closes in In";
                clock.classList.add('success-text')

                if (timeUntilClockInCloses < 0) {
                    clockInStatus.innerHTML = "Clock In Closed"
                    timeUntilClockInCloses = Math.abs(shiftTime - currentTime)
                    clock.classList.remove('success-text')
                    clock.classList.add('failure-text')
                    clockInButton.classList.add('btn-clock-in-late')
                }

                timeUntilClockInCloses = timeUntilClockInCloses / 1000;
                let durationForShiftClosing = totalDuration(timeUntilClockInCloses)

                // find the first instance of time that is greater than 1:
                let currentTimeStatus = durationForShiftClosing.find(item => item.totalTime >= 1)
                clockInTime.innerHTML = currentTimeStatus.totalTime
                currentTimeStatus.totalTime > 1
                    ? clockInIdentifier.innerHTML = currentTimeStatus.plural : clockInIdentifier.innerHTML = currentTimeStatus.singular;
            } else {
                let shiftEnds = new Date(clockInTime.getAttribute('data-shift-ending-time'));
                let timeUntilShiftEnds = shiftEnds - currentTime
                clockInStatus.innerHTML = "Shift Ends In"
                clock.classList.add('pending-text')
                clockInButton.classList.add('btn-on-shift')
                clockInButton.disabled = true

                timeUntilShiftEnds = timeUntilShiftEnds / 1000;
                let durationForShiftEnding = totalDuration(timeUntilShiftEnds);
                console.log(durationForShiftEnding)
                // find the first instance of time that is greater than 1
                // todo: move to function
                let currentTimeStatus = durationForShiftEnding.find(item => item.totalTime >= 1)
                clockInTime.innerHTML = currentTimeStatus.totalTime
                currentTimeStatus.totalTime > 1
                    ? clockInIdentifier.innerHTML = currentTimeStatus.plural : clockInIdentifier.innerHTML = currentTimeStatus.singular;
            }

        }

    }
}

manipulateClockInDateDisplay();