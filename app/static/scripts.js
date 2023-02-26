function handleSpinner(event) {
    document.getElementById('spinner').style.visibility = 'visible';
    }


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
