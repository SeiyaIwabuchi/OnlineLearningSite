$(window).load(init());

function init() {
  // ログイン認証
  $("#bt_login").click(function() {
    var authData = JSON.stringify({ 
        "loginID":$("#ID").val(),
        "pass":$("#passwd").val()
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
          alert("ログインIDまたはパスワードが間違っています。")
        }
      }});
  });
}