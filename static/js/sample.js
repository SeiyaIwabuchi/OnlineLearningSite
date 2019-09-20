$(window).load(init());

function init() {
  $("#RorW").hide();
  $("#Correct").hide();
  $("#next").hide();
  $("#Comment").hide();
  $("#解説").hide();
  $("#ansButton").click(function() {
    var textData = JSON.stringify(
      { "radio1":$("input[name=rad]:checked").val() === "1",
        "radio2":$("input[name=rad]:checked").val() === "2",
        "radio3":$("input[name=rad]:checked").val() === "3",
        "radio4":$("input[name=rad]:checked").val() === "4"
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
          $("#Correct").text("正答 : " + JSON.parse(data.ResultSet).correct);
          $("#Comment").text(JSON.parse(data.ResultSet).comment);
          $("#ansButton").hide();
        }
      });
    }else{
      alert("必ず回答してください。");
    }
    return false;
  });
  $("#next").click(function() {
    var textData = "";
    $.ajax({
      type:'POST',
      url:'/nextPoroblem',
      data:textData,
      contentType:'application/json',
      success:function(data) {
        if(JSON.parse(data.ResultSet).finsh == "false"){
          //ここで問題書き換えと隠すものは隠す
          //表示するもの
          $("#ansButton").show();
          //隠すもの
          $("#RorW").hide();
          $("#Correct").hide();
          $("#next").hide();
          $("#Comment").hide();
          $("#解説").hide();
          //内容を書き換えるもの
          //問題と選択肢はjsonで受け取ったものを使う
          $("#problem").text(JSON.parse(data.ResultSet).problem);
          $("#radio1Label").text(JSON.parse(data.ResultSet).choice1);
          $("#radio2Label").text(JSON.parse(data.ResultSet).choice2);
          $("#radio3Label").text(JSON.parse(data.ResultSet).choice3);
          $("#radio4Label").text(JSON.parse(data.ResultSet).choice4);
          $("#radio1").prop('checked', false);
          $("#radio2").prop('checked', false);
          $("#radio3").prop('checked', false);
          $("#radio4").prop('checked', false);
          $("input:[name=rad]").attr("checked",false);
        }else{
          window.location.href = "/result";
        }
      }
    });
  });
  $("#getMyResult").click(function(){
    window.location.href = "/result";
  });
}