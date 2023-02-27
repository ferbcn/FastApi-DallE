//var moreImages = new WebSocket("ws://127.0.0.1:8000/moreImages");
var moreImages = new WebSocket("wss://art-intel.site:443/moreImages");


var imageOffset = 5;
var imageQueue = [];

// On Init load first 5 images into queue buffer
document.addEventListener("DOMContentLoaded", function(event) {
    // Get first queue elements
    moreImages.send(imageOffset);
    imageOffset += 5;
    waitingForImage = true;
});


// window scroll detect
// Load queue with images
window.onscroll = function() {

    if (window.innerHeight + window.pageYOffset >= document.body.offsetHeight - 1000) {

        // Pre: Images are loaded in the queue
        // load new images into queue
        // if queue is emtpy load waiting spinner
        if (imageQueue.length < 5){
            moreImages.send(imageOffset);
            imageOffset += 5;
        }
        // if we have images in the queue buffer add them to dom
        if (imageQueue.length > 0){
            // add image element to container
            var imageFeed = document.getElementById("image_child");
            var newImage = imageQueue[imageQueue.length-1];
            imageFeed.appendChild(newImage);
            imageQueue.pop(newImage)
            console.log("Image with ID " + newImage.id + " added to DOM")
        }
        // if queue is empty, load spinner
        else{
            var element = document.getElementById("spinner");
            //element.style.position = "absolut";
            element.style.top = "500px";
            element.style.visibility = 'visible';
        }

    }
}

// add images to queue buffer
moreImages.onmessage = function(event) {

    document.getElementById('spinner').style.visibility = 'hidden';

    jsonString = event.data;
    jsonData = JSON.parse(jsonString);
    imgTitle = jsonData.title;
    imgId = jsonData.id;
    imgData64 = jsonData.rendered_data;
    imgDescription = jsonData.description;

    var newImage = document.createElement('div');
    newImage.classList.add('outer_image_field');
    newImage.classList.add('image_field');

    // add title
    var title = document.createElement('h3');
    title.appendChild(document.createTextNode(imgTitle));

    // add image
    var img = document.createElement('img');
    img.src = "data:image;base64," + imgData64;

    var text = document.createElement('div');
    text.appendChild(document.createTextNode(imgDescription));

    // add close button to image
    var cross = document.createElement('a');
    cross.classList.add('close-icon');
    cross.href = "javascript:handleDelete(" + imgId + ")";

    newImage.appendChild(title);
    newImage.appendChild(cross);
    newImage.appendChild(img);
    newImage.appendChild(text);
    newImage.id = imgId

    // add image to queue
    imageQueue.push(newImage);
    console.log("Image with ID " + newImage.id + " added to Queue")
}


// Hide (and delete if logged in) of images in the feed
function handleDelete(imageId){
    // delete image from DOM
    const image = document.getElementById(imageId);
    const list = document.getElementById("image_child");
    list.removeChild(image);

    // make post request (for deletion from DB)
    var url = "/delete/?image_id=" + imageId;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    // Send the proper header information along with the request
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    //xhr.setRequestHeader("accept", "application/json");
    xhr.send("");
}
