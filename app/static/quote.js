var q2i = new WebSocket("ws://0.0.0.0:8000/q2i");
// var ws = new WebSocket("wss://art-intel.site/ws");

function handleClick(event) {
    event.preventDefault();
    document.getElementById('spinner').style.visibility = 'visible';
    var quote = document.getElementById("quote").innerHTML;
    var author = document.getElementById("author").innerHTML;
    q2i.send(quote);
}

function handleDelete(image_id){
    const image = document.getElementById(image_id);
    const list = document.getElementById("quoteImage");
    list.removeChild(image);
    // socket.emit('delete_event', {data: image_id});
}

var img_id = 1;

q2i.onmessage = function(event) {

    document.getElementById('spinner').style.visibility = 'hidden';
    //console.log(event)
    //json_string = event.data;
    //json_data = JSON.parse(json_string);
    //console.log(json_data);

    var img_url = event.data;
    console.log("URL: " + img_url);

    // add image element to container
    var quote_image = document.getElementById("quoteImage");

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
    quote_image.appendChild(new_image);

}


//const submitBtn = document.querySelector('button[type="submit"]');
//const form = document.querySelector('form');

