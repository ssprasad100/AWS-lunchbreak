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

        var timeoutId, previousValue;

        var init = function() {
            field.on('keydown', function(event) {
                switch(event.which) {
                    case KEY_ARROW_UP:
                        select(-1);
                        return;
                        break;
                    case KEY_ARROW_DOWN:
                        select(1);
                        return;
                        break;
                    case KEY_ARROW_RIGHT:
                        return;
                        break;
                    case KEY_ARROW_LEFT:
                        return;
                        break;
                }

                console.log(event.which);

                var value = field.val();
                console.log('value: ' + value);

                if(!value || value == previousValue)
                    return;

                previousValue = value;

                window.clearTimeout(timeoutId);
                timeoutId = window.setTimeout(function() {
                    console.log('triggered');
                    service.getQueryPredictions(
                        {
                            input: value
                        },
                        autocomplete
                    );
                }, TIMEOUT);
            });
        };

        var getSelectedItem = function() {
            var children = fieldAutocomplete.children();
            for(var i = 0; i < children.length; i++) {
                if($(children[i]).hasClass('selected'))
                    return i;
            }
            return -1;
        };

        var select = function(direction) {
            var children = fieldAutocomplete.children();
            if(children.length == 0)
                return;

            var currentIndex = getSelectedItem();
            console.log('currentIndex: ' + currentIndex);
            if(currentIndex >= 0) {
                var current = $(children[currentIndex]);
                current.removeClass('selected');
            }

            var nextIndex = 0;
            if(children.length != currentIndex)
                nextIndex = currentIndex + direction;
            if(currentIndex < 0 && nextIndex < currentIndex)
                nextIndex = children.length + direction;
            console.log('nextIndex: ' + nextIndex);

            var text;
            if((nextIndex < 0 && nextIndex < currentIndex) || nextIndex == children.length)
                text = previousValue;
            else {
                var next = $(children[nextIndex]);
                next.addClass('selected');
                text = next.text();
            }

            field.val(text);
            field[0].focus();
            field[0].setSelectionRange(previousValue.length, text.length, 'forward');


            // if(nextIndex < 0)
            //     nextIndex = children.length + direction;
            // else if(nextIndex == children.length)
            //     nextIndex = 0;
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
