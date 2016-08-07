(function() {
    'use strict';

    var SearchField = function() {

        var TIMEOUT = 250,
            KEY_ARROW_LEFT = 37,
            KEY_ARROW_UP = 38,
            KEY_ARROW_RIGHT = 39,
            KEY_ARROW_DOWN = 40,
            KEY_ENTER = 13;

        var field = $('#store-search');
        var fieldContainer = field.parent();
        var fieldAutocomplete = fieldContainer.nextAll();
        var form = fieldContainer.parent();
        var service = new google.maps.places.AutocompleteService();
        var geocoder = new google.maps.Geocoder;

        var timeoutId, previousValue;

        var init = function() {
            getCurrentLocation();
            registerEvents();
        };

        var registerEvents = function() {
            var autocompleteSelector = '.search-box-autocomplete li';

            $(document).on('click', autocompleteSelector, function(event) {
                field.val(this.textContent);
                form.submit();
            });

            $(document).on('mouseover', autocompleteSelector, function(event) {
                field.val(this.textContent);
            });

            $(document).on('mouseleave', autocompleteSelector, function(event) {
                field.val(previousValue);
            });

            field.on('keyup', function(event) {
                switch(event.which) {
                    case KEY_ARROW_UP:
                        move(-1);
                        return;
                        break;
                    case KEY_ARROW_DOWN:
                        move(1);
                        return;
                        break;
                    case KEY_ARROW_RIGHT:
                        return;
                        break;
                    case KEY_ARROW_LEFT:
                        return;
                        break;
                }

                var value = field.val();

                if(!value) {
                    fieldAutocomplete.hide();
                    return;
                }

                if(value == previousValue)
                    return;

                previousValue = value;

                window.clearTimeout(timeoutId);
                timeoutId = window.setTimeout(function() {
                    service.getQueryPredictions(
                        {
                            input: value
                        },
                        autocomplete
                    );
                }, TIMEOUT);
            });
        };

        var getCurrentLocation = function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    geocoder.geocode(
                        {
                            'location': {
                                lat: position.coords.latitude,
                                lng: position.coords.longitude
                            }
                        }, function(results, status) {
                            if(status === 'OK' && results[0]) {
                                if(!field.val())
                                    field.val(results[0].formatted_address);
                            }
                        }
                    );

                }, function(error) {
                    // Error
                }, {
                    timeout: 10000,
                    maximumAge: 30 * 60 * 1000
                });
            }
        };

        var getSelectedItem = function() {
            var children = fieldAutocomplete.children();
            for(var i = 0; i < children.length; i++) {
                if($(children[i]).hasClass('selected'))
                    return i;
            }
            return -1;
        };

        var move = function(direction) {
            var children = fieldAutocomplete.children();
            var currentIndex = getSelectedItem();

            var nextIndex = 0;
            if(children.length != currentIndex)
                nextIndex = currentIndex + direction;
            if(currentIndex < 0 && nextIndex < currentIndex)
                nextIndex = children.length + direction;

            select(nextIndex);

        };

        var select = function(index) {
            var children = fieldAutocomplete.children();
            if(children.length == 0)
                return;

            var currentIndex = getSelectedItem();
            if(currentIndex >= 0) {
                var current = $(children[currentIndex]);
                current.removeClass('selected');
            }

            var text;
            if((index < 0 && index < currentIndex) || index == children.length)
                text = previousValue;
            else {
                var next = $(children[index]);
                next.addClass('selected');
                text = next.text();
            }

            field.val(text);
            field[0].focus();
            field[0].setSelectionRange(previousValue.length, text.length, 'forward');
        };

        var autocomplete = function(predictions, status) {
            if(status != google.maps.places.PlacesServiceStatus.OK)
                return;

            var autocompleteHtml = '';

            for(var i = 0; i < predictions.length; i++) {
                var prediction = predictions[i];
                autocompleteHtml += '<li>' + prediction.description + '</li>';
            }

            fieldContainer.addClass('active');
            fieldAutocomplete.show();
            fieldAutocomplete.html(autocompleteHtml);
        };

        init();
    };

    $(document).ready(function() {
        SearchField();
    });
})();
