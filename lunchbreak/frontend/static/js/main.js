//@prepros-prepend include/*.js
//@prepros-prepend photoswipe/*.min.js

var playing = false;

var interval = setInterval(nextSlideshow, 4000);
function nextSlideshow() {
	// Afgaan en kijken welke binnen scroll bereik zijn
	var scroll = $(window).scrollTop();
	var screenHeight = $( window ).height();
	$('.slideshow').each(function() {
		var top = $(this).offset().top;
		var myHeight = $(this).outerHeight();
		if (scroll > top - screenHeight/2 && scroll < top + myHeight/2){
			var selected = $(this).find(".controls div.selected");
			var volgende = selected.next("div");
			if (volgende.length == 0){
				volgende = $(this).find(".controls div").first();
			}
			pressedControl(volgende);
		}
		
	});

}
function pressedControl(who){
	clearInterval(interval);
	interval = setInterval(nextSlideshow, 4000);
	// data krijgen
	var content = who.html();
	var newImage = $(content).clone(); 
	newImage.hide();
	
	var slideshow = who.closest(".slideshow");
	var view = slideshow.find(".view");
	var old = view.children();
	view.append(newImage);
	newImage.fadeIn("fast", function(){
		old.fadeOut("fast", function(){
			$(this).remove();
		});
	});
	slideshow.find(".controls div.selected").removeClass("selected");
	who.addClass("selected");
}
$( document ).ready(function() {
	lastScrollTop = $(document).scrollTop();
	
	$('input, textarea').placeholder();
    $(window).scroll(function () {
    	if (!playing){
    		var scroll = $(window).scrollTop();
    		if (scroll > $('#header').outerHeight()/2){
    			playing = true;
    			if ($('#video').length == 1){
    				$('#video').get(0).play();
    			}
    		}
    	}
    });
    
        
 	$('a').click(function(e){
 		if ($(this).is('#toon-deelnemende-winkels')){
 			return;
 		}
 		var tag = $(this).attr('href').charAt(0);
 		if (tag == '#'){
 			var top = $($(this).attr('href')).offset().top;
 			if ($('#menu').length > 0){
 				top -= $('#menu').outerHeight();
 			}
 			$('html, body').animate({
 	           scrollTop: top
 	       }, 1000);
 	       e.preventDefault();
 	       return false;
 		}
 	});
 	pressedolanguage = false;
 	$(document).click(function() {
 		if (pressedolanguage){
 			pressedolanguage = false;
 			return;
 		}
 		pressedolanguage = false;
 		if ($('.language-popover').is(':visible')){
 			$('.language-popover').fadeOut('fast');
 		}
 	});
 	$('.language-popover').click(function(event){
 		pressedolanguage = true;
 	});
 	$('.language-selector').click(function(){
 		if (!$('.language-popover').is(':visible')){
	 		$('.language-popover').fadeIn('fast');
	 	}else{
	 		$('.language-popover').fadeOut('fast');
	 	}
	 	pressedolanguage = true;
 	});
 	$('#submit-location').click(function(e){
		getLocation();
		e.preventDefault();
		return false;
	});
	$('#submit-ghent').click(function(e){
		$('#latitude').remove();
		$('#longitude').remove();
		$('.input_hid').remove();
		$('form').first().submit();
		e.preventDefault();
		return false;
	});
	
	$('#toon-deelnemende-winkels').click(function(e){
		$('#deelnemende-winkels').stop().slideDown('fast');
		e.preventDefault();
		return false;
	});
	$('.slideshow .controls div.selected').each(function() {
		var slideshow = $(this).closest(".slideshow");
		var view = slideshow.find(".view");
		$(this).html(view.html());
	});
	$('.slideshow .controls div').click(function(e) {
		pressedControl($(this));
	});
	
	
	// Menu balk
	
	if ($('#menu').hasClass("transparent")){
		var menu = $('#menu');
		overlay = menu.clone();
		overlay.attr("id", "");
		overlay.removeClass("transparent");
		overlay.addClass("white");
		overlay.addClass("isHidden");
		var menu_height = menu.outerHeight()+10; // fix
		overlay.css("top", "-"+menu_height+"px");
		menu.parent().after(overlay);
		
		menuHidden = true;
		
		$(window).scroll(function(){
			didScroll();
		});
	}
	
	$('.smartphone-menu-buttons .button').click(function() {
		// Menu uitklappen
		showSmartphoneMenu();
	});
	$('#smartphone-menu .close').click(function() {
		// Menu uitklappen
		var smenu = $('#smartphone-menu');
		smenu.fadeOut('fast');
	});
	
	$('.slideshow .ipad .view').click(function(){
		slideshow = $(this).closest(".slideshow");
		// Lijst maken van alle screenshots
		var items = [];
		var index = 0;
		var startIndex = 0;
		slideshow.find(".controls div").each(function(){
			if ($(this).is(".selected")){
				startIndex = index;
			}
			items.push({
				src: $(this).find('img').attr('data-photoswipe-src'),
				msrc: $(this).find('img').attr('data-photoswipe-src'),
				w: $(this).find('img').attr('data-photoswipe-width'),
				h: $(this).find('img').attr('data-photoswipe-height')
			});
			index++;
		});
		var options = {
			index: startIndex,
			getThumbBoundsFn: function(index){
				var object = slideshow.find('.ipad, .iphone').first();
				var offset = object.offset();
				return {x: offset.left, y: offset.top, w:object.outerWidth()};
			},
			bgOpacity: 1,
			loop: false,
			fullscreenEl: false,
			shareEl: false
		};
		var pswpElement = document.querySelectorAll('.pswp')[0];
		
		var gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, items, options);
		gallery.init();
	
	});
	
});
function didScroll(){
	var height = $(document).scrollTop();
	
	/*var difference = height - lastScrollTop;
	lastScrollTop = height;*/
	
	// Balk overlay
	var menu = $('#menu');
	var transparent = $('#menu.transparent');
	
	if (height > 50){	
		showMenu();
	}else{
		// Transparant menu verbergen!
		hideMenu();
	}
}
function showMenu(){
	if (menuHidden){
		menuHidden = false;
		overlay.removeClass("isHidden");
		overlay.stop().animate({top: 0}, "fast");
	}
}
function hideMenu(){
	if (!menuHidden){
		menuHidden = true;
		var menu_height = overlay.outerHeight();
		overlay.addClass("isHidden");
		overlay.stop().animate({top: -menu_height}, "fast");
	}
}



function showSmartphoneMenu() {
	var menu = $('#menu .menu-items');
	var content = menu.html();
	var smenu = $('#smartphone-menu');
	$('#smartphone-menu-content').html(content);
	smenu.fadeIn("fast");
	// Scrollen blokkeren
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(locationUpdate, locationFailed);
    } else { 
        $('#error').html('Locatievoorzieningen zijn niet ondersteund op deze browser. Zoek in de buurt van Gent.');
    }
}

function locationUpdate(position) {
	$('#latitude').val(position.coords.latitude);
	$('#longitude').val(position.coords.longitude);
	$('.input_hid').remove();
    $('form').first().submit();
}
function locationFailed(error){
	 $('#error').html('We kunnen je huidige locatie niet bepalen. Zoek in de buurt van Gent.');
}

