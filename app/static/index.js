//var moreImages = new WebSocket("ws://192.168.1.111:8000/moreImages");
var moreImages = new WebSocket("wss://art-intel.site:443/moreImages");


var current_image_offset = 5;
var waiting_for_image = false;


function handleDelete(image_id){
    const image = document.getElementById(image_id);
    const list = document.getElementById("image_child");
    list.removeChild(image);

    // make post request
    //var url = "/delete/";
    //var params = "?image_id=" + image_id;
    var url = "/delete/?image_id=" + image_id;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    // Send the proper header information along with the request
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    //xhr.setRequestHeader("accept", "application/json");
    xhr.send("");
}


document.addEventListener("DOMContentLoaded", function(event) {
    // Get first queue elements
    moreImages.send(current_image_offset);
    current_image_offset += 5;
    waiting_for_image = true;
});


// window scroll detect
// Load queue with images
window.onscroll = function() {

    if (window.innerHeight + window.pageYOffset >= document.body.offsetHeight - 1000 && waiting_for_image == false) {

        // Pre: Images are loaded in the queue
        // load new images into queue
        moreImages.send(current_image_offset);
        current_image_offset += 5;
        waiting_for_image = true;

        // if queue is emtpy load waiting spinner
        var element = document.getElementById("spinner");
        //element.style.position = "absolut";
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
    // if list is too long remove top item
    /*
    if (generatedImage.childNodes.length > 40){
        var first = generatedImage.firstElementChild;
        generatedImage.removeChild(first);
    }
    */
    generatedImage.appendChild(new_image);
    console.log("Image with ID " + img_id + " added to DOM")

}