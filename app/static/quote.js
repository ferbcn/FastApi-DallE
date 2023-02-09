function handleClick(event) {
    event.preventDefault();
    document.getElementById('spinner').style.visibility = 'visible';

    var msg = {
        type: "message",
        text: document.getElementById("input_text").innerHTML,
        title: document.getElementById("author").innerHTML,
    };

    // Send the msg object as a JSON-formatted string.
    text2image.send(JSON.stringify(msg));
    //text2image.send(text);
}