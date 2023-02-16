

function getClockInLatLong(){

    const clockInMessage = document.getElementById('clock-in-message');
    let clockInButton = document.getElementById("clock-in-button");

    function success(position){
        const latitude = position.coords.latitude
        const longitude = position.coords.longitude;
        let hxValsData = `{"shift-activated": "True", "latitude": ${latitude}, "longitude": ${longitude}}`;
        let hxTargetData = "#shift-activation-section"
        let hxSelectData = "#shift-activation-section"
        let hxSwapData ="multi:#shift-activation-section,#clock-in-starts:outerHTML"
        let hxPostData = clockInButton.getAttribute('jx-post');
        clockInButton.removeAttribute('jx-post');


        clockInButton.setAttribute("hx-vals", hxValsData)
        clockInButton.setAttribute('hx-target', hxTargetData);
        clockInButton.setAttribute('hx-swap', hxSwapData)
        clockInButton.setAttribute('hx-post', hxPostData)
        clockInButton.removeAttribute('onclick')
        let content = document.createTextNode("Clock In");
        clockInButton.innerHTML = "";
        clockInButton.appendChild(content);
        htmx.process(clockInButton)
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
            clockInButton.innerHTML = "";
            clockInButton.appendChild(document.createTextNode('Locating...'))
            navigator.geolocation.getCurrentPosition(success, error);
        }

}

// document.querySelector('#clock-in-button').addEventListener('click', getClockInLatLong);
// document.body.addEventListener('htmx:afterSettle', getClockInLatLong)