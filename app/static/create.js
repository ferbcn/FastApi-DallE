function handleClick(event) {
    event.preventDefault();
    document.getElementById('spinner').style.visibility = 'visible';
    var text = document.getElementById("input_text").value;

    var msg = {
        type: "message",
        text: document.getElementById("input_text").value,
        title: document.getElementById("title").value,
    };

    // Send the msg object as a JSON-formatted string.
    text2image.send(JSON.stringify(msg));
    //text2image.send(text);
}