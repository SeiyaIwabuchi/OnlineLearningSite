$(window).load(init());

function init() {
    $(".problemList").click(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2] + "/ProblemList.html";
    });
    $(".returnToProblem").onclick(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2];
    });
    $(".playAgain").onclick(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2] + "/deleteRecord";
    });
    $(".playAgainOnlyMistakes").onclick(function(){
        window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2] + "/onlyMistakes";
    });
}
