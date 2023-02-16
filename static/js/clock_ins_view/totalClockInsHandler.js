function manipulateStatus(){
    const status = document.getElementsByClassName("clock-in-table")
    for (const element of status){
        const statusIdentifier = element.getElementsByClassName('status-identifier')[0];
        const statusIcon = element.getElementsByClassName('status-icon-indicator')[0];
        const statusText = element.getElementsByClassName("status-text")[0];
        // todo: BEFORE PRODUCTION — OTHER ICONS
        switch (statusIdentifier.textContent) {
            case "LTE":
                statusIcon.innerHTML = "cancel";
                statusIcon.classList.add("md-red");
                statusText.innerHTML = "Late";
                statusText.classList.add("failure-text");
                break;
            case "EA":
                statusIcon.innerHTML = "check_circle";
                statusIcon.classList.add("md-green");
                statusText.innerHTML = "Early";
                statusText.classList.add("success-text");
                break;
            case "DSP":
                statusIcon.innerHTML = "pause_circle";
                statusIcon.classList.add("md-green");
                statusText.innerHTML = "Pending";
                statusText.classList.add("pending-text");
                break;
        }
        console.log(statusIdentifier)
    }
}

manipulateStatus();

document.getElementById('user-content').addEventListener('htmx:afterRequest', function(evt){
    if(document.getElementById("clock-ins-this-month")){
        manipulateStatus();
    }
})


