$(window).load(init());

function init() {
  $("#RorW").hide();
  $("#Correct").hide();
  $("#next").hide();
  $("#ansButton").click(function() {
    var textData = JSON.stringify(
      { "radio1":$("input[name=rad]:checked").val() === "1",
        "radio2":$("input[name=rad]:checked").val() === "2",
        "radio3":$("input[name=rad]:checked").val() === "3",
        "radio4":$("input[name=rad]:checked").val() === "4",
        "sessionID":$("#sessionID").text()
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
          var result = JSON.parse(data.ResultSet).result;
          $("#hello").text(result);
        }
      });
    }else{
      alert("必ず回答してください。");
    }
    return false;
  });
}