//var text2image = new WebSocket("ws://192.168.1.111:8000/text2image");
//var text2image = new WebSocket("wss://art-intel.site:443/text2image");

function handleSpinner(event) {
    document.getElementById('spinner').style.visibility = 'visible';
    }

function handleDelete(image_id){
    const image = document.getElementById(image_id);
    const list = document.getElementById("generatedImage");
    list.removeChild(image);
}
