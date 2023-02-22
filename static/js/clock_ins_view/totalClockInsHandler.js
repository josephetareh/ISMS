function manipulateStatus(){
    const status = document.getElementsByClassName("clock-in-table");
    console.log("hello")
    for (const element of status){
        const statusIdentifier = element.getElementsByClassName('status-identifier')[0];
        const statusIcon = element.getElementsByClassName('status-icon-indicator')[0];
        const statusText = element.getElementsByClassName("status-text")[0];
        // todo: BEFORE PRODUCTION — OTHER ICONS
        switch (statusIdentifier.textContent) {
            case "LTE":
                statusIcon.textContent = "cancel";
                statusIcon.classList.add("md-red");
                statusText.textContent = "Late";
                statusText.classList.add("failure-text");
                break;
            case "EA":
                statusIcon.textContent = "check_circle";
                statusIcon.classList.add("md-green");
                statusText.textContent = "Early";
                statusText.classList.add("success-text");
                break;
            case "DSP":
                statusIcon.textContent = "pause_circle";
                statusIcon.classList.add("md-orange");
                statusText.textContent = "Pending";
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


