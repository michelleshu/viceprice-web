/****** sliding menu ********/
$menu_visible  = false;
$(document).on('click', '.sliding', function(){
    if ($menu_visible){
        $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
        $(".right-side-bar").hide("slide", { direction: "right" }, 700);
        $(".sliding").animate({ right: "0"} , 700);
        $menu_visible=false;
    }
    else{
        $(".slider-arrow").attr("src", "../static/img/right-arrow.png");
        $(".right-side-bar").show("slide", { direction: "right" }, 700);
        $(".sliding").animate({ right: "25%"} , 700);
        $menu_visible=true;
    }
});

$(document).ready(function() {
    $("#location-cover-photo").load(function(){
        // Resize according to offset and Facebook cover photo proportions
        var originalWidth = $(this).width();
        var originalHeight = $(this).height();

        var xOffset = $(this).attr("data-x-offset");
        var yOffset = $(this).attr("data-y-offset");

        var clipTop = (yOffset * 0.01) * originalHeight;
        var clipLeft = (xOffset * 0.01) * originalWidth;

        // Do not clip narrower than sidebar width
        clipLeft = Math.min(clipLeft, $(this).width() - $(".right-side-bar").width());
        if (clipLeft < 0) { clipLeft = 0; }

        var clipBottom = (originalHeight - clipTop) - 0.37 * (originalWidth - clipLeft);

        if (clipBottom < 0) {
            clipTop += clipBottom;
            clipBottom = 0;
        }

        $(this).css("-webkit-clip-path", "inset(" + clipTop + "px 0px "  + clipBottom + "px "  + clipLeft + "px)");
        $(this).css("margin-top", "-" + clipTop + "px");
        $(this).css("margin-bottom", "-" + clipBottom + "px");
    });
});

