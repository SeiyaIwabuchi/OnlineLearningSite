$(window).load(init());

function init() {
  $("#RorW").hide();
  $("#Correct").hide();
  $("#next").hide();
  $("#ansButton").click(function() {
    var textData = JSON.stringify({"radio1":$("input[name=rad]:checked").val() === "1","radio2":$("input[name=rad]:checked").val() === "2","radio3":$("input[name=rad]:checked").val() === "3","radio4":$("input[name=rad]:checked").val() === "4"});
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
    return false;
  });
}