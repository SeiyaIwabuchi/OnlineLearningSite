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
        url:'/authRegistry',
        data:authData,
        contentType:'application/json',
        success:function(data) {
          alert("登録しました。");
          location.href = "/";
        }});
    }else{
      alert("登録回数が超過しました。");
    }
  });
}