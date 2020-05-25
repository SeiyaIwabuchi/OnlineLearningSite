$(window).load(init());

function init() {
    $("#subjTextBox").hide();
    $(".mngButton").click(function(){
        var id = $(this).attr('id');
        if(id.split("_")[1] == "del"){
            console.log(id.split("_")[0] + "を削除します。");
        }else if(id.split("_")[1] == "mod"){
            console.log($("#" + id.split("_")[0] + "_text").val() + "に変更します。");
        }
    });
    $("#loginButton").click(function(){
        if($("#subjTextBox").css("display") == "block"){
            if($("#subjTextBox").val() != ""){
                console.log($("#subjTextBox").val());
                window.location.href=location.href + "/addSubj/" + $("#subjTextBox").val();
            }
        }else{
            $("#subjTextBox").show();
        }
    });
}