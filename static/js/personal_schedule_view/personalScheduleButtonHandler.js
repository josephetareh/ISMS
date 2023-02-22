function personalScheduleHandler(){
    let queryString = window.location.search;
    if (queryString){
         const pageParameters = new URLSearchParams(queryString);
        if (pageParameters.has("activity")){
            const activityParameter = pageParameters.get("activity")
            let activeButton = document.querySelector("#activity-selection :nth-child(1)")
            let currentActiveButton = document.querySelectorAll(".active-activity")
            currentActiveButton.forEach(currentActiveActivity => {
                currentActiveActivity.classList.remove("active-activity");
            })
            switch (activityParameter){
                case "CS":
                    activeButton = document.getElementById("class-list-button");
                    activeButton.classList.add("active-activity");
                    break;
                case "MT":
                    activeButton = document.getElementById("meeting-list-button");
                    activeButton.classList.add("active-activity");
                    break;
                case "PT":
                    activeButton = document.getElementById("personal-training-list-button");
                    activeButton.classList.add("active-activity");
                    break;
                default:
                    activeButton.classList.add("active-activity");
            }
        }
    } else {
        const allActivitiesButton = document.querySelector("#activity-selection :nth-child(1)");
        allActivitiesButton.classList.add("active-activity")
    }
}

personalScheduleHandler()
// document.body.addEventListener("htmx:pushedIntoHistory", personalScheduleHandler);

document.body.addEventListener("htmx:pushedIntoHistory", function (evt){
    if(document.getElementById('staff-schedule')){
        personalScheduleHandler()
    }
});
// window.addEventListener("load", function(evt){
//     if(document.getElementById('staff-schedule')){
//         personalScheduleHandler()
//     }
// });