// var text2image = new WebSocket("ws://192.168.1.111:8000/text2image");
var text2image = new WebSocket("wss://art-intel.site/text2image");


function handleDelete(image_id){
    const image = document.getElementById(image_id);
    const list = document.getElementById("generatedImage");
    list.removeChild(image);
}

var img_id = 1;

text2image.onmessage = function(event) {

    document.getElementById('spinner').style.visibility = 'hidden';
    //console.log(event)
    //json_string = event.data;
    //json_data = JSON.parse(json_string);
    //console.log(json_data);

    var img_url = event.data;
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

