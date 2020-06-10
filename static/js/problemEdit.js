$(window).load(init());

function init() {
    var accessToken = location.href.split("/")[location.href.split("/").length-4];
    var subName = location.href.split("/")[location.href.split("/").length-3];
    var mode = location.href.split("/")[location.href.split("/").length-2];
    var probNum = location.href.split("/")[location.href.split("/").length-1];
    $("#fButton").click(function(){
        var probNum = Number(location.href.split("/")[location.href.split("/").length-1])-1;
        window.location.href = "/mngProblem/" + location.href.split("/")[location.href.split("/").length-4] + "/" + location.href.split("/")[location.href.split("/").length-3] + "/" + "mod/" + probNum;
    });
    $("#bButton").click(function(){
        var probNum = Number(location.href.split("/")[location.href.split("/").length-1])+1;
        window.location.href = "/mngProblem/" + location.href.split("/")[location.href.split("/").length-4] + "/" + location.href.split("/")[location.href.split("/").length-3] + "/" + "mod/" + probNum;
    });
    $("#doneButton").click(function(){
        var textData = JSON.stringify(
            {
                "subName":decodeURI(subName),
                "probNum":probNum,
                "mode":mode,
                "problemStatement":$("#problemText").val(),
                "choise1":$("#No1").val(),
                "choise2":$("#No2").val(),
                "choise3":$("#No3").val(),
                "choise4":$("#No4").val(),
                "correctAnswer":$("#NumberSelecter").val(),
                "coment":$("#comentTextArea").val()
            }
        );
        $.ajax({
            type:'POST',
            url:"/" + accessToken + "/posting",
            data:textData,
            contentType:'application/json',
            success:function(data) {
                location.href = "/mngProblem/" + accessToken + "/" + subName;
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                alert("HTTPステータス:" + XMLHttpRequest.status  + "\nエラー内容:" + textStatus);
                //location.reload();
            }
          });
    });
    $("#cancel").click(function(){
        location.href = "/mngProblem/" + accessToken + "/" + subName;
    });
    $("#continue").click(function(){
        var textData = JSON.stringify(
            {
                "subName":decodeURI(subName),
                "probNum":probNum,
                "mode":mode,
                "problemStatement":$("#problemText").val(),
                "choise1":$("#No1").val(),
                "choise2":$("#No2").val(),
                "choise3":$("#No3").val(),
                "choise4":$("#No4").val(),
                "correctAnswer":$("#NumberSelecter").val(),
                "coment":$("#comentTextArea").val()
            }
        );
        $.ajax({
            type:'POST',
            url:"/" + accessToken + "/posting",
            data:textData,
            contentType:'application/json',
            success:function(data) {
                location.href = "/mngProblem/" + accessToken + "/" + subName + "/add/dummy"
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                alert("HTTPステータス:" + XMLHttpRequest.status  + "\nエラー内容:" + textStatus);
                //location.reload();
            }
          });
    });
}