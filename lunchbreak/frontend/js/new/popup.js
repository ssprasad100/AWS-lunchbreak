$(document).ready(function() {
    pressedPopup = null;

    $(document).click(function() {
        if (pressedPopup) {
            $(".popup.container").not(pressedPopup).removeClass("open");
            pressedPopup = null;
            return;
        }

        $(".popup.container").removeClass("open");
    });

    $("a.popup.anchor").click(function(e) {
        e.preventDefault();

        var container = $(this).parents(".popup.container");
        container.toggleClass("open");
        pressedPopup = container[0];
    });

    $('.popup.box').click(function(event) {
        var container = $(this).parents(".popup.container");
        pressedPopup = container[0];
    });

    $('.popup.box a').click(function(event) {
        var container = $(this).parents(".popup.container");
        container.removeClass("open");
    });
});
