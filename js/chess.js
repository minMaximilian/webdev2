let sessionId;
let request;
let request_2;
let chess;
let error;
var input;

document.addEventListener("DOMContentLoaded", init, false);
document.addEventListener("keyup", move)

function loadCookie(cookie_retrieve) {
    var cookies = document.cookie.split("; ");
    var x = null
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].split("=")
        if (cookie[0] == cookie_retrieve) {
            x = cookie[1]
            break
        }    
    }
    return x
}

function render() {
    request = new XMLHttpRequest();
    request.addEventListener("readystatechange", handle_render, false);
    request.open("GET", "render.py?cookie=" + sessionId, true);
    request.send();
}

function handle_render() {
    if (request.readyState === 4 && request.status === 200) {
        if (request.responseText != "error") {
            chess.innerHTML = request.responseText
        }
    }
}

function move(n) {
    if (n["key"] === "Enter") {
        request_2 = new XMLHttpRequest();
        request_2.addEventListener("readystatechange", handle_move, false);
        request_2.open("GET", "move.py?cookie=" + sessionId + "&move=" + input.value.slice(0, 4), true);
        request_2.send();
        input.value = null
    }
}

function handle_move() {
    if (request_2.readyState === 4 && request_2.status === 200) {
        error.innerHTML = request_2.responseText
    }
}

function init() {
    chess = document.getElementById("chess")
    error = document.getElementById("error")
    input = document.getElementById("input")
    sessionId = loadCookie("sessionId")
    render()
    window.setInterval(render, 2000);
}