$(window).load(init());
var subURL = "";
function init() {
  $('#subjectList').change(function() {
    subURL = $('option:selected').val();
  })
  $('#start').on('click', function() {
    //window.location.href = subURL;
    if (confirm('ページ遷移しますか？')) {
      window.location.href = subURL.valueOf();
    }
  });
}