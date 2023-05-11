async function analyse_comments(comment_source) {
    // change button to have bootstrap spinner while analysing comment data.
    document.getElementById(`analyse_${comment_source}_comments_button_body`).classList.add("spinner-border", "spinner-border-sm");
    document.getElementById(`analyse_${comment_source}_comments_button`).disabled = true;
    document.getElementById(`analyse_${comment_source}_comments_button_text`).textContent = "Analysing...";
    // prepare data to send to the endpoint.
    let input = document.getElementById(`${comment_source}_comments_input`);
    let data = new FormData()
    data.append("input", input.value)
    // use fetch api to send request and return a response.
    fetch(`${window.origin}/analyse_comments/${comment_source}`, {
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
        // use DOMParser to parse string into a DOM Document.
        let parser = new DOMParser();
        let doc = parser.parseFromString(html, "text/html");
        let analyserResult = document.querySelector(`#analyser_${comment_source}_result`);
        analyserResult.innerHTML = doc.body.innerHTML;
    }).catch(function (error) {
        console.error(`Error analysing ${comment_source} comments: ${error.message}`);
    });
    // revert button after 1 second.
    setTimeout(() => {
        document.getElementById(`analyse_${comment_source}_comments_button_body`).classList.remove("spinner-border", "spinner-border-sm");
        document.getElementById(`analyse_${comment_source}_comments_button`).disabled = false;
        document.getElementById(`analyse_${comment_source}_comments_button_text`).textContent = "Analyse";
    }, 1000)
}
