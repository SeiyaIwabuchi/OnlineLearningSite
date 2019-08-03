$(window).load(init());

function init() {
  // POSTでアップロード
  $("#btnUpLoad").click(function() {
    var formdata = new FormData($('#my_form').get(0));
    $.ajax({
      url  : "/upProblem",
      type : "POST",
      data : formdata,
      cache       : false,
      contentType : false,
      processData : false,
      dataType    : "html"
    })
    .done(function(data, textStatus, jqXHR){
      alert(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      alert("fail");
    });
  });
  $(window).on("beforeunload", function(e) {
    $.ajax({
      url  : "/deleteAdminURL/" + $(location).attr('pathname').split("/")[2],
      type : "GET",
      async: false
    });
  });
}