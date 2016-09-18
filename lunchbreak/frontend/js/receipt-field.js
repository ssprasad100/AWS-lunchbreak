(function() {

    var ReceiptField = function() {
        this.openingperiods = JSON.parse(weekday_openingperiods_json);
        this.element = $('#checkout-receipt');
        this.dropdown = this.element.find('select').first();
        this.input = this.element.find('input').first();
        this.subscript = this.element.find('.subscript').last();
        this.openinghours = this.subscript.find('.openinghours').first();

        this.init = function() {
            var self = this;
            this.dropdown.change(function() {
                self.onWeekdayChange();
            });
        };

        this.onWeekdayChange = function() {
            var weekday = this.dropdown.val();
            this.openinghours.text(
                this.openingperiods[weekday]
            );
        };

        this.init();
    };

    $(document).ready(function() {
        new ReceiptField();
    });
})();
