(function($) {
"use strict";

/* ==============================================
ANIMATION -->
=============================================== */

    new WOW({
	    boxClass:     'wow',      // default
	    animateClass: 'animated', // default
	    offset:       0,          // default
	    mobile:       true,       // default
	    live:         true        // default
    }).init();

/* ==============================================
LIGHTBOX -->
=============================================== */   

  jQuery('a[data-gal]').each(function() {
    jQuery(this).attr('rel', jQuery(this).data('gal')); });     
    jQuery("a[data-rel^='prettyPhoto']").prettyPhoto({animationSpeed:'slow',theme:'light_square',slideshow:false,overlay_gallery: true,social_tools:false,deeplinking:false});


/* ==============================================
SCROLL -->
=============================================== */

$(function() {
  $('a[href*=#]:not([href=#])').click(function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      var target = $(this.hash);
	  var section_pos = target.offset().top;
	  var h4_pos = target.offset().top - target.height() - 52;
	  var elempos = "";
	  if ( target.hasClass( "section" ) ) {
		  elempos = section_pos;
	  }
	  else {
		  elempos = h4_pos;
	  }
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
	  console.log(target);
      if (target.length) {
        $('html,body').animate({
          scrollTop: elempos
        }, 1000);
        return false;
      }
    }
  });
});

/* ==============================================
VIDEO FIX -->
=============================================== */

    $(document).ready(function(){
      // Target your .container, .wrapper, .post, etc.
      $(".media").fitVids();
    });

})(jQuery);