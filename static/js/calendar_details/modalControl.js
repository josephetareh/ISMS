import anime from '/static/ISMS_NODE/node_modules/animejs/lib/anime.es.js'
function manipulateStartSessionsListings(){
    let sessionStartControlButtons = document.getElementsByClassName("session-control");
    let defaultStartButton = document.getElementById("start-session").childNodes[1];
    let selectedUsers = new Set();
    for (const controlButton of sessionStartControlButtons){
        controlButton.addEventListener("click", function(evt){
            selectedUsers = swapButtonInfo(controlButton, selectedUsers);
            updateSessionButton("start-session", selectedUsers, "start",
                "starting", "Start", defaultStartButton)
        })
    }
}

function manipulateEndSessionsListings(){
    let sessionEndControlButtons = document.getElementsByClassName("end-session-control");
    let defaultEndButton = document.getElementById("end-session").childNodes[1];
    for (const controlButton of sessionEndControlButtons){
        controlButton.addEventListener("click", function (evt){
            let selectedUsers = new Set();
            let currentlySelected = document.getElementsByClassName("success-mini-board");
            for (let userButton of currentlySelected){
                swapButtonInfo(userButton, selectedUsers)
            }
            selectedUsers = swapButtonInfo(controlButton, selectedUsers);
            updateSessionButton("end-session", selectedUsers, "end",
                "ending", "End", defaultEndButton)
        })
    }

}


function swapButtonInfo(buttonToManipulate, selectedUsers){
    let myIcon = buttonToManipulate.childNodes[1];
    let sessionClient = buttonToManipulate.childNodes[5];
    let trainingID = buttonToManipulate.getAttribute("data-selected-user-id")
    if (buttonToManipulate.classList.contains("failure-mini-board")){
        buttonToManipulate.classList.remove("failure-mini-board");
        buttonToManipulate.classList.add("success-mini-board");
        myIcon.classList.remove("md-red");
        myIcon.classList.add("md-green");
        sessionClient.classList.remove("failure-text");
        sessionClient.classList.add("success-text");
        selectedUsers.add(trainingID);
    } else if(buttonToManipulate.classList.contains("success-mini-board")){
        buttonToManipulate.classList.add("failure-mini-board");
        buttonToManipulate.classList.remove("success-mini-board");
        myIcon.classList.add("md-red");
        myIcon.classList.remove("md-green");
        sessionClient.classList.add("failure-text");
        sessionClient.classList.remove("success-text");
        selectedUsers.delete(trainingID);
    }
    return selectedUsers;
}


function updateSessionButton(divNodeID, selectedUsers, sessionUpdateType, sessionUpdateTypePresent, sessionUpdateTypeTitle, defaultStartButton){
    let currentSessionButtonNode = document.getElementById(divNodeID).childNodes[1];
    let currentSessionButtonNodeID = currentSessionButtonNode.getAttribute("id");
    if (selectedUsers.size >= 1){
        if (currentSessionButtonNodeID === `${sessionUpdateType}-session-for-all-btn`){
            // replace the update button
            let myUpdatedButton = document.createElement("button");
            myUpdatedButton.setAttribute("id", `${sessionUpdateType}-session-for-selected-btn`);
            myUpdatedButton.classList.add("btn-alt-ghost", "d-flex", "flex-row", "align-items-center", "py-4", "px-7");
            let myUpdatedButtonIcon = document.createElement("span");
            myUpdatedButtonIcon.classList.add("material-symbols-outlined", "md-green", "md-36");
            myUpdatedButtonIcon.textContent = "group";
            myUpdatedButton.appendChild(myUpdatedButtonIcon);
            myUpdatedButtonIcon.insertAdjacentText('afterend',`${sessionUpdateTypeTitle} Session for Selected`);
            document.getElementById(`${sessionUpdateType}-session`).replaceChild(myUpdatedButton, defaultStartButton);
        }
        let updatingSessionFor = {};
        updatingSessionFor[`${sessionUpdateTypePresent}-session-for`] = [...selectedUsers].join(", ")
        let newSelectionButton = document.getElementById(`${sessionUpdateType}-session-for-selected-btn`);
        newSelectionButton.setAttribute("hx-vals", JSON.stringify(updatingSessionFor));
        newSelectionButton.setAttribute("hx-post", defaultStartButton.getAttribute("hx-post"));
        newSelectionButton.setAttribute("data-bs-dismiss", "modal");
        newSelectionButton.setAttribute("hx-select", "#user-content");
        newSelectionButton.setAttribute("hx-target", "#user-content");
        newSelectionButton.setAttribute("hx-swap", "outerHTML");
        htmx.process(newSelectionButton);
    } else if(selectedUsers.size === 0) {
        if (currentSessionButtonNodeID === `${sessionUpdateType}-session-for-selected-btn`){
            document.getElementById(`${sessionUpdateType}-session`).replaceChild(defaultStartButton, currentSessionButtonNode);
        }
    }
}

manipulateStartSessionsListings();
manipulateEndSessionsListings();

document.body.addEventListener("htmx:afterSettle", function(evt){
    if (document.getElementById("session-details")){
        manipulateStartSessionsListings();
        manipulateEndSessionsListings();
    }
})

