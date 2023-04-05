async function analyseComment() {
    // change button to have bootstrap spinner
    document.getElementById("analyseButtonBody").classList.add("spinner-border", "spinner-border-sm");
    document.getElementById("analyseButton").disabled = true;
    document.getElementById("analyseText").textContent = "Analysing...";
    // analyse comment
    let comment_textarea = document.getElementById('commentInput');
    let data = new FormData()
    data.append("comment", comment_textarea.value)
    fetch(`${window.origin}/classify`, {
        method: "POST",
        credentials: "include",
        body: data,
        cache: "no-cache",
    }).then(function (response) {
        if (!response.ok) {
            throw new Error(`Response status was not 200-299: ${response.status}`)
        }
        return response.text()
    }).then(function (html) {
        let parser = new DOMParser();
        let doc = parser.parseFromString(html, "text/html");
        let prediction = doc.getElementById("resultHeading").textContent;
        if (prediction >= 0.5) {
            doc.querySelector("#resultHeading").textContent = "Misinformation";
            doc.querySelector("#predictedClassification").setAttribute("value","Misinformation");
            doc.getElementById("result").classList.add("alert-danger");
        } else {
            doc.querySelector("#resultHeading").textContent = "Neutral";
            doc.querySelector("#predictedClassification").setAttribute("value","Neutral");
            doc.getElementById("result").classList.add("alert-success");
        }
        console.log(doc.getElementById("predictedClassification").value)
        let analyserResult = document.querySelector('#analyserResult');
        analyserResult.innerHTML = doc.body.innerHTML;
    }).catch(function (error) {
        console.error(`Error analysing comment: ${error.message}`);
    });
    // revert button
    setTimeout(() => {
        document.getElementById("analyseButtonBody").classList.remove("spinner-border", "spinner-border-sm");
        document.getElementById("analyseButton").disabled = false;
        document.getElementById("analyseText").textContent = "Analyse";
    }, 1000)
}

