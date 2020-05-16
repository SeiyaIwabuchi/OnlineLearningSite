$(window).load(init());

function init() {
    $(".problemList").click(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2] + "/ProblemList.html";
    });
    $(".returnToProblem").click(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2];
    });
    $(".playAgain").click(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2] + "/deleteRecord";
    });
    $(".playAgainOnlyMistakes").click(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2] + "/onlyMistakes";
    });
}
