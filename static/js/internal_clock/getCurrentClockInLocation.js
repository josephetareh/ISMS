function getClockInLatLong(){

    const clockInMessage = document.getElementById('clock-in-message');
    let clockInButton = document.getElementById("clock-in-status");

    function success(position){
        const latitude = position.coords.latitude
        const longitude = position.coords.longitude;
        let hxData = `{"shift-activated": "True", "latitude": ${latitude}, "longitude": ${longitude}}`;
        clockInButton.setAttribute("hx-vals", hxData)
        let content = document.createTextNode("Clock In")
        clockInButton.appendChild(content)

    }

    function error(){
        let content = document.createTextNode("The System Could Not Detect Your Location to Activate Your Clock In." +
            " Please Turn on Your Location Services to Mark Your Clock in");
        clockInMessage.appendChild(content);
    }

        if(!navigator.geolocation) {
            let content = document.createTextNode("GeoLocation is not supported by your browser, " +
                "please visit the super admin to report this issue");
            clockInMessage.appendChild(content);
        } else {
            // remove the disabled status from the button if the clock is enabled
            if (clockInButton.hasAttribute('data-button-status')){
                if (clockInButton.getAttribute("data-button-status") === "clock-in-enabled"){
                    let content = document.createTextNode("Loading");
                    clockInButton.appendChild(content);
                    clockInButton.disabled = false
                }
            }
            navigator.geolocation.getCurrentPosition(success, error);
        }

}

window.addEventListener("load", getClockInLatLong);