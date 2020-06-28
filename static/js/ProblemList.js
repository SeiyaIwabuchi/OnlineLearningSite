$(window).load(init());

function init() {
    $(".returnToProblem").click(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2];
    });
}
