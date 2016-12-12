$(document).ready(function() {
    $('a').click(function(e) {
        if (!$(this).attr('href')) {
            return;
        }

        var tag = $(this).attr('href').charAt(0);
        if (tag == '#') {
            var top = $($(this).attr('href')).offset().top;
            if ($('#menu').length > 0) {
                top -= $('#menu').outerHeight();
            }

            var current = $('body').scrollTop();

            $('html, body').stop(true);
            $('html, body').animate({
                scrollTop: top
            }, 1000);
            e.preventDefault();
            return false;
        }
    });

    // Stop all scroll animations when the user scrolls
    // wheel = standard, DOMMouseScroll + mousewheel = deprecated event
    $('html, body').bind('wheel DOMMouseScroll mousewheel', function() {
        $('html, body').stop(true);
    });
});
