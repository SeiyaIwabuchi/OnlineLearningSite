$(window).load(init());

function init() {
    if (location.href.split("/")[location.href.split("/").length-1] != "None"){
        $('#subSelecter').val(decodeURI(location.href.split("/")[location.href.split("/").length-1]));
    }
    $('#subSelecter').change(function() {
        var r = $('option:selected').val();
        if(r != ""){
            window.location.href = "/mngProblem/" + location.href.split("/")[location.href.split("/").length-2] + "/" + r;
        }
    });
    $(".mngButton").click(function(){
        var id = $(this).attr('id');
        console.log(id);
        if(id.split("_")[1] == "del"){
            console.log(id.split("_")[0] + "を削除します。");
        }else if(id.split("_")[1] == "mod"){
            console.log(id.split("_")[0] + "を変更します。");
        }
    });
}