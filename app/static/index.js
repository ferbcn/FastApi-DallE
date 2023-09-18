var imageOffset = 5;
var imageQueue = [];

var isScrollingBack = false;
var isAuth = false;

function setJSAuthorization(auth){
    isAuth = auth;
    if (isAuth) console.log("User Authorized!");
    else console.log("User Not authorized!");
};

var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
wsUrl = ws_scheme + '://' + window.location.host + "/moreImages"

// Open WebSocket
var moreImages = new WebSocket(wsUrl);


moreImages.onopen = (event) => {
    console.log("Socket open!");
    // On init load first 5 images into queue buffer
    document.addEventListener("DOMContentLoaded", function(event) {
        // Get first queue elements
        moreImages.send(imageOffset);
        imageOffset += 5;
    });
    console.log("First image request sent!");

};

// add images to queue buffer
moreImages.onmessage = function(event) {

    // hide spinner animation
    document.getElementById('spinner').style.visibility = 'hidden';

    jsonString = event.data;
    jsonData = JSON.parse(jsonString);
    imgTitle = jsonData.title;
    imgId = jsonData.id;
    imgDescription = jsonData.description;
    imgUrl = jsonData.filename;

    var newImage = document.createElement('div');
    newImage.classList.add('outer_image_field');
    newImage.classList.add('image_field');
    // add title
    var title = document.createElement('h3');
    title.appendChild(document.createTextNode(imgTitle));
    // add image
    var img = document.createElement('img');
    //img.src = "data:image;base64," + imgData64;
    img.src = imgUrl;
    var text = document.createElement('div');
    text.appendChild(document.createTextNode(imgDescription));
    // add close button to image
    var cross = document.createElement('a');
    cross.classList.add('close-icon');
    cross.href = "javascript:handleDelete(" + imgId + ")";

    newImage.appendChild(title);
    if (isAuth){
        newImage.appendChild(cross);
    }
    newImage.appendChild(img);
    newImage.appendChild(text);
    newImage.id = imgId

    // add image to queue
    imageQueue.push(newImage);
    console.log("Image with ID " + newImage.id + " added to Queue")
};

moreImages.onclose = function(event) {
    console.log('Socket closed, reopening...');
    setTimeout(function() {moreImages = new WebSocket(wsUrl);}, 1000);
};

moreImages.onerror = function(err) {
    console.error('Socket encountered error: ', err.message, 'Closing socket');
    ws.close();
};


// window scroll detect
// Load queue with images
window.onscroll = function() {

    // make scroll to top button visible
    var myBtn = document.getElementById("myBtn");
    if (window.pageYOffset < 800) {
        myBtn.style.visibility = 'hidden';
    }
    else{
        myBtn.style.visibility = 'visible';
    }

    // console.log(imageQueue.length);
    if (window.innerHeight + window.pageYOffset >= document.body.offsetHeight) {
        // Pre: Images are loaded in the queue
        // if queue is emtpy load request new images over ws
        if (imageQueue.length < 5){
            moreImages.send(imageOffset);
            console.log("Image request sent with offset " + imageOffset);
            imageOffset += 5;
        }
        // if we have images in the queue buffer add them to dom
        if (imageQueue.length > 0){
            // add image element to container
            var imageFeed = document.getElementById("image_child");
            var newImage = imageQueue[imageQueue.length-1];
            imageFeed.appendChild(newImage);
            imageQueue.pop(newImage);
            console.log("Image with ID " + newImage.id + " added to DOM");

        }
        // if queue is empty, load spinner
        else{
            var element = document.getElementById("spinner");
            element.style.top = "500px";
            element.style.visibility = 'visible';
            // reset flag in case of network issues
        }
    }
}

// Hide and deletion of images in the feed
function handleDelete(imageId){
    // delete image from DOM
    const image = document.getElementById(imageId);
    const list = document.getElementById("image_child");
    list.removeChild(image);

    // make post request (for deletion from DB), user needs to be authorized
    var url = "/delete/?image_id=" + imageId;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    // Send the proper header information along with the request
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    //xhr.setRequestHeader("accept", "application/json");
    xhr.send("");
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}