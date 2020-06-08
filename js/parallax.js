var parallax_1;
var parallax_1_speed



document.addEventListener("DOMContentLoaded", init, false);
window.addEventListener("scroll", translate);

function init () {
    parallax_1 = document.querySelector(".parallax_1");
    parallax_1_speed = parallax_1.getAttribute("data-speed");
    parallax_1.style.transform = "translate3d(0px, 375px, 0px)";
}

function translate () {
    let ypos = window.scrollY;
    let pd1 = ((parallax_1_speed/100) * ypos) + 375;
    parallax_1.style.transform = "translate3d(0px, " + pd1 + "px, 0px)";
};