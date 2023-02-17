//var text2image = new WebSocket("ws://192.168.1.111:8000/text2image");
var text2image = new WebSocket("wss://art-intel.site:443/text2image");

function handleSpinner(event) {
    document.getElementById('spinner').style.visibility = 'visible';
    }

function handleClick(event) {
    event.preventDefault();
    document.getElementById('spinner').style.visibility = 'visible';

    if (window.location.pathname == '/create/'){
        var msg = {
            type: "message",
            text: document.getElementById("input_text").value,
            title: document.getElementById("title_author").value,
        };
    }
    else{
        var msg = {
            type: "message",
            text: document.getElementById("input_text").innerHTML,
            title: document.getElementById("title_author").innerHTML,
        };
    }

    // Send the msg object as a JSON-formatted string.
    console.log(msg);

    text2image.send(JSON.stringify(msg));
    //text2image.send(text);
}

function handleDelete(image_id){
    const image = document.getElementById(image_id);
    const list = document.getElementById("generatedImage");
    list.removeChild(image);
}

var img_id = 1;

text2image.onmessage = function(event) {

    document.getElementById('spinner').style.visibility = 'hidden';
    //console.log(event)
    json_string = event.data;
    json_data = JSON.parse(json_string);
    console.log(json_data);

    //var img_url = event.data;
    var img_url = json_data.img_url;
    console.log("URL: " + img_url);

    // add image element to container
    var new_image = document.createElement('div');
    // add image
    var img = document.createElement('img');
    img.src = img_url;
    new_image.appendChild(img);
    // add delete link
    var del_text = document.createElement('a');
    img_id += 1;
    del_text.href = "javascript:handleDelete(" + img_id + ")";
    del_text.appendChild(document.createTextNode("Hide"));
    new_image.appendChild(del_text);
    new_image.id = img_id

    // add image element to container
    var generatedImage = document.getElementById("generatedImage");
    generatedImage.appendChild(new_image);

}


//const submitBtn = document.querySelector('button[type="submit"]');
//const form = document.querySelector('form');

