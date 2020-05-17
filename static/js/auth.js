$(window).load(init());

function init() {
  // ログイン認証
  var loginNum = 0;
  $("#bt_login").click(function() {
    loginNum++;
    if(loginNum <= 3){
      var authData = JSON.stringify({
          "loginID":$("#ID").val(),
          "pass":$("#passwd").val(),
          "sessionID":$("#sessionID").text()
        });
      $.ajax({
        type:'POST',
        url:'/auth',
        data:authData,
        contentType:'application/json',
        success:function(data) {
          if(JSON.parse(data.ResultSet).Result == "True"){
            window.location.href = "/" + location.href.split("/")[location.href.split("/").length-2] + JSON.parse(data.ResultSet).adminURL;
          }else{
            alert("ログインIDまたはパスワードが間違っています。");
          }
        }});
    }else{
      alert("ログイン試行回数が超過しました。");
    }
  });
}