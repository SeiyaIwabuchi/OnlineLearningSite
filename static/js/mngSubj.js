$(window).load(init());

function init() {
    $(".mngButton").click(function(){
        var id = $(this).attr('id');
        if(id.split("_")[1] == "del"){
            console.log(id.split("_")[0] + "を削除します。");
        }else if(id.split("_")[1] == "mod"){
            console.log($("#" + id.split("_")[0] + "_text").val() + "に変更します。");
        }
    });
}