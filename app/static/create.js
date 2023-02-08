function handleClick(event) {
    event.preventDefault();
    document.getElementById('spinner').style.visibility = 'visible';
    var text = document.getElementById("input_text").value;
    text2image.send(text);
}