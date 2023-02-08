var moreImages = new WebSocket("ws://192.168.1.111:8000/moreImages");
// var ws = new WebSocket("wss://art-intel.site/ws");

var last_img_id;
var current_image_offset = 10; // Initially 10 images are loaded onto the html tamplate
var waiting_for_image = false;


function handleDelete(image_id){
    const image = document.getElementById(image_id);
    const list = document.getElementById("image_child");
    list.removeChild(image);
}


// ON start 5 images are loaded into the queue
var image_queue = [];

document.addEventListener("DOMContentLoaded", function(event) {
    // Get first queue elements
    moreImages.send(current_image_offset);
    current_image_offset += 1;
    waiting_for_image = true;
});


// window scroll detect
// Load queue with images
window.onscroll = function() {

    if (window.innerHeight + window.pageYOffset >= document.body.offsetHeight && waiting_for_image == false) {

        // Pre: Images are loaded in the queue
        // load new images into queue
        moreImages.send(current_image_offset);
        waiting_for_image = true;

        // if queue is emtpy load waiting pinner
        var element = document.getElementById("spinner");
        element.style.position = "absolut";
        element.style.top = "500px";
        element.style.visibility = 'visible';

    }
}

// add images to feed
// remove images from queue
moreImages.onmessage = function(event) {

    waiting_for_image = false;
    document.getElementById('spinner').style.visibility = 'hidden';

    json_string = event.data;
    json_data = JSON.parse(json_string);
    img_title = json_data.title;
    img_id = json_data.id;
    img_data_b64 = json_data.rendered_data;

    var new_image = document.createElement('div');
    // add title
    new_image.innerHTML += "<center><h3>" + img_title + "</h3></center>";
    new_image.classList.add('image_field');
    // add image
    var img = document.createElement('img');
    img.src = "data:image;base64," + img_data_b64;
    new_image.appendChild(img);
    // add delete link
    var del_text = document.createElement('a');
    del_text.href = "javascript:handleDelete(" + img_id + ")";
    del_text.appendChild(document.createTextNode("Hide"));
    new_image.appendChild(del_text);
    new_image.id = img_id

    // add image element to container
    var generatedImage = document.getElementById("image_child");
    generatedImage.appendChild(new_image);
    console.log("Image with ID " + img_id + " added to DOM")

}