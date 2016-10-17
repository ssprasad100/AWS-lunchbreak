(function() {
    'use strict';

    $(document).ready(function() {
        // storeLocation is defined in the template
        var map = new google.maps.Map(
            $('#confirm')[0],
            {
                'zoom': 15,
                'center': storeLocation
            }
        );
        var marker = new google.maps.Marker({
            'position': storeLocation,
            'map': map
        })
    });
})();
