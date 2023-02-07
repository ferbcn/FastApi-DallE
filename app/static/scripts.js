function handleClick() {
    document.getElementById('spinner').style.visibility = 'visible';
}

//var ws = new WebSocket("ws://localhost:8000/ws");
var ws = new WebSocket("wss://art-intel.site/ws");

var startTime;

ws.onmessage = function(event) {
    var endTime = new Date();
    var rtt = endTime - startTime;
    var messages = document.getElementById('messages')
    var message = document.createElement('li')
    var text = event.data;
    if (!isNaN(rtt)){
        text += " (RTT: " + rtt + "ms)";
    }
    var content = document.createTextNode(text);
    message.appendChild(content);
    messages.appendChild(message);
}

function sendMessage(event) {
    var input = document.getElementById("messageText");
    startTime = new Date();
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}