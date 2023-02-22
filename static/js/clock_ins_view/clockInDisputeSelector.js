function clockInDisputeSelectorHandling(){
    const selectedObjects = new Set();
    const checkBoxes = document.getElementsByClassName("form-check-input");
    const disputeButton = document.getElementById('clock-in-dispute-button');

    for (const checkbox of checkBoxes){
        checkbox.addEventListener("change", function(evt){
            if (evt.target.checked){
                selectedObjects.add(checkbox.id)
                disputeButton.disabled = false;
            } else {
                selectedObjects.delete(checkbox.id);
            }
            if (selectedObjects.size === 1) {
                disputeButton.textContent = "Dispute 1 Clock In "
            } else if (selectedObjects.size > 1){
                disputeButton.textContent = `Dispute ${selectedObjects.size} Clock Ins`
            } else if (selectedObjects.size <= 0) {
                disputeButton.disabled = true;
                disputeButton.textContent = "Dispute Clock In "
            }
            // let hxValsData = `{"shift-activated": "True", "latitude": ${latitude}, "longitude": ${longitude}}`;
            let setAsString = "";
            let setAsArray = Array.from(selectedObjects)
            setAsArray.forEach(function(value, index){
                if (index === setAsArray.length-1){
                    setAsString += value + "\""
                } else {
                    setAsString += value + ", "
                }
            })
            let hxValues = `{"dispute-ids": "${setAsString}}`


            disputeButton.setAttribute('hx-vals', hxValues)


        })
    }
}
clockInDisputeSelectorHandling();

