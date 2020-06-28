$(window).load(init());

function init() {
  // ログイン認証
  var loginNum = 0;
  $("#bt_login").click(function() {
    const shaObj = new jsSHA("SHA-256", "TEXT");
    shaObj.update($("#ID").val());
    const hashedID = shaObj.getHash("HEX");
    shaObj.update($("#passwd").val());
    const hashedPW = shaObj.getHash("HEX");
    loginNum++;
    if(loginNum <= 3){
      var authData = JSON.stringify({
          "loginID":hashedID,
          "pass":hashedPW,
          "sessionID":$("#sessionID").text()
        });
      $.ajax({
        type:'POST',
        url:'/auth',
        data:authData,
        contentType:'application/json',
        success:function(data) {
          if(JSON.parse(data.ResultSet).Result == "True"){
            window.location.href = JSON.parse(data.ResultSet).adminURL;
          }else{
            alert("ログインIDまたはパスワードが間違っています。");
          }
        }});
    }else{
      alert("ログイン試行回数が超過しました。");
    }
  });
}