/****** sliding menu ********/
$menu_visible  = false; 
$(".sliding").click(function(){   
    if ($menu_visible){ 
        $(".slider-arrow").attr("src", "../static/img/left-arrow.png");
        $(".right-side-bar").hide("slide", { direction: "right" }, 700);
        $(".sliding").animate({ right: "0"} , 700);
        $menu_visible=false;
    }else
    {
        $(".slider-arrow").attr("src", "../static/img/right-arrow.png");
        $(".right-side-bar").show("slide", { direction: "right" }, 700);
        $(".sliding").animate({ right: "25%"} , 700);
        $menu_visible=true;
    }
});
