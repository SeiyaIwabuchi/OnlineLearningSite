$(window).load(init());

function init() {
    $("#subject").click(function(){
        window.location.href = "/mngSubject/" + location.href.split("/")[location.href.split("/").length-1];
    });
}