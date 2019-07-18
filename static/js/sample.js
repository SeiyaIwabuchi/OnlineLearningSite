$(window).load(init());

function init() {
  $("#RorW").hide();
  $("#Correct").hide();
  $("#next").hide();
  $("#Comment").hide();
  $("#解説").hide();
  var probNum = 0;
  $("#ansButton").click(function() {
    var textData = JSON.stringify(
      { "radio1":$("input[name=rad]:checked").val() === "1",
        "radio2":$("input[name=rad]:checked").val() === "2",
        "radio3":$("input[name=rad]:checked").val() === "3",
        "radio4":$("input[name=rad]:checked").val() === "4",
        "sessionID":$("#sessionID").text(),
        "probNum":probNum
      });
    var answered = false;
    if( $("input[name=rad]:checked").val() == "1" || 
        $("input[name=rad]:checked").val() == "2" || 
        $("input[name=rad]:checked").val() == "3" || 
        $("input[name=rad]:checked").val() == "3" || 
        $("input[name=rad]:checked").val() == "4")
    {
      answered = true;
    }
    if(answered){
      $.ajax({
        type:'POST',
        url:'/postText',
        data:textData,
        contentType:'application/json',
        success:function(data) {
          //$("#hello").text(result);
          //判定がtrueだったら解説と正答は表示しない。
          var RorWMsg = "不正解";
          $("#next").show();
          $("#RorW").show();
          if(JSON.parse(data.ResultSet).RorW){
            RorWMsg = "正解";
          }else{
            $("#Correct").show();
            $("#Comment").show();
            $("#解説").show();
          }
          $("#RorW").text(RorWMsg);
          $("#Correct").text("正解 : " + JSON.parse(data.ResultSet).correct);
          $("#Comment").text(JSON.parse(data.ResultSet).comment);
        }
      });
    }else{
      alert("必ず回答してください。");
    }
    return false;
  });
  $("#next").click(function() {
    alert("未実装ですぅぅ。");
    probNum = probNum + 1;
    var textData = JSON.stringify({
      "requestProblem":probNum
    });
    $.ajax({
      type:'POST',
      url:'/nextPoroblem',
      data:textData,
      contentType:'application/json',
      success:function(data) {
        //ここで問題書き換えと隠すものは隠す
      }
    });
  });
}