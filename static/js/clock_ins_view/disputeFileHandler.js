function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes'

    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}


function getFilesFromUpload(){
    const inputButtons = document.getElementsByClassName("btn-alt-ghost");
     for (let button of inputButtons){
         button.addEventListener("change", function(evt){
             let buttonID = button.getAttribute("for");
             let buttonIndex = buttonID.slice(-1);

             if (evt.target.files.length > 0){
                 const filesUploaded = evt.target.files;

                 let filesUploadedSection = document.getElementById(`uploaded-files-${buttonIndex}`);
                 filesUploadedSection.textContent = "";
                 for (let disputeFile of evt.target.files){
                     console.log(disputeFile.size)
                     let warningContent = document.getElementById(`file-upload-warning-${buttonIndex}`)
                     let submitButton =  document.getElementById(`submit-button-${buttonIndex}`)
                     let disputeForm = document.getElementById(`dispute-form-${buttonIndex}`)

                     function disableFormSubmission(evt){
                         // todo: this is not working, but at least currently handled by disabled
                        evt.preventDefault();
                    }

                     if (!warningContent.hasAttribute("d-none")){
                           warningContent.classList.add("d-none");
                           warningContent.textContent = "";
                           submitButton.disabled = false;
                           disputeForm.removeEventListener("submit", disableFormSubmission)
                     }

                     if (disputeFile.size > 32000000) {
                         let warningContent = document.getElementById(`file-upload-warning-${buttonIndex}`)
                         warningContent.classList.remove("d-none")
                         warningContent.textContent  =
                             "Warning. You Cannot Upload a File that is Greater than 32MB to the server. Please upload a new set of files to continue"

                         submitButton.disabled = true;

                         disputeForm.addEventListener("submit", disableFormSubmission)
                     }

                     const fileElement = document.createElement("div");
                     fileElement.classList.add("transparent-board", "mini-board", "py-6", "px-7", "d-flex", "flex-row", "me-5", "mt-7");

                     const fileIcon = document.createElement("span");
                     fileIcon.classList.add("material-symbols-outlined", "md-36", "md-grey", "me-4")

                     const fileInfoContainer = document.createElement("div");
                     fileInfoContainer.classList.add("d-flex", "flex-column", "zero-point-eight-seven-five-root");

                     const fileName = document.createElement("div");
                     fileName.classList.add("medium")
                     const fileSize = document.createElement("div");
                     fileSize.classList.add("extra-light", "subtext-shade")

                     const fileDivider = document.createElement("div");
                     fileDivider.classList.add("file-divider", "mt-7", "ms-5", "me-7", "px-1", "py-6");

                     filesUploadedSection.append(fileElement, fileDivider);

                     switch(disputeFile.type) {
                         case "audio/mpeg":
                             // append file icon information
                             fileIcon.textContent = "graphic_eq"
                             break;
                         case "image/jpeg":
                         case "image/png":
                         case "image/gif":
                         case "image/svg+xml":
                              fileIcon.textContent = "image"
                             break;
                         case "application/pdf":
                             fileIcon.textContent = "picture_as_pdf";
                             break;
                         default:
                             fileIcon.textContent = "folder"
                             break;
                     }
                   // set file name and file size into the DOM
                     fileInfoContainer.append(fileName, fileSize);
                     fileElement.append(fileIcon, fileInfoContainer)

                     let disputeFileName = disputeFile.name;
                     if (disputeFileName.length > 32){
                        fileName.textContent  = `${disputeFile.name.substring(0, 32)} ...`
                     } else {
                         fileName.textContent = `${disputeFile.name}`
                     }
                     let totalSize = formatBytes(disputeFile.size)

                     fileSize.textContent = `${totalSize}`

                 }
             }

         })
     }
}

getFilesFromUpload();