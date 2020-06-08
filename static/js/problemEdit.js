$(window).load(init());

function init() {
    $("#fButton").click(function(){
        var probNum = Number(location.href.split("/")[location.href.split("/").length-1])-1;
        window.location.href = "/mngProblem/" + location.href.split("/")[location.href.split("/").length-4] + "/" + location.href.split("/")[location.href.split("/").length-3] + "/" + "mod/" + probNum;
    });
    $("#bButton").click(function(){
        var probNum = Number(location.href.split("/")[location.href.split("/").length-1])+1;
        window.location.href = "/mngProblem/" + location.href.split("/")[location.href.split("/").length-4] + "/" + location.href.split("/")[location.href.split("/").length-3] + "/" + "mod/" + probNum;
    });
    $("#doneButton").click(function(){

    });
}