(function() {

    var ReceiptField = function() {
        this.element = $('#checkout-receipt');
        this.dropdown = this.element.find('select').first();
        this.openingperiods = this.dropdown.data('openingperiods');
        this.input = this.element.find('input').first();

        this.openinghoursSubscript = this.element.find('.subscript.openinghours').first();
        this.openinghours = this.openinghoursSubscript.find('#openinghours').first();

        this.group = null;
        this.groupDeadline = this.element.find('.subscript.group_deadline').first();
        this.deadline = this.groupDeadline.find('#deadline').first();
        this.receipt = this.groupDeadline.find('#receipt').first();

        this.init = function() {
            var self = this;
            this.dropdown.change(function() {
                self.onWeekdayChange();
            });
            this.onWeekdayChange();
        };

        /**
         * callback for when the day of order is changed.
         */
        this.onWeekdayChange = function() {
            var hasGroup = this.group !== null;
            this.openinghoursSubscript.toggle(!hasGroup);
            this.input.prop('readonly', hasGroup);
            this.groupDeadline.toggle(hasGroup);
            var delivery = hasGroup && this.group.delivery;
            this.element.find('.receipt-type').text(
                delivery ? 'levering' : 'afhaling'
            );

            if (hasGroup) {
                this.input.val(this.group.receipt);
                this.deadline.text(this.group.deadline);
                var receiveText = this.group.receipt + ' ' + (delivery ? 'geleverd' : 'afgehaald');
                this.receipt.text(receiveText);
            } else {
                var weekday = this.dropdown.val();
                this.openinghours.text(
                    this.openingperiods[weekday]
                );
            }
        };

        /**
         * Callback received from GroupField when its group changes.
         * @param  {?object} group Simple group information or null.
         */
        this.onGroupChange = function(group) {
            this.group = group;
            this.onWeekdayChange();
        };

        this.init();
    };

    var GroupField = function(receiptField) {
        this.receiptField = receiptField;
        this.element = $('#checkout-group');
        /**
         * Dictionary of group ids and their delivery, receipt, and deadline fields.
         *
         * {
         *     '1': {
         *         'deadline': '11:00',
         *         'receipt': '11:45',
         *         'delivery': true
         *     }
         * }
         *
         * @type {object}
         */
        this.groups = this.element.data('groups');
        this.dropdown = this.element.find('select').first();

        this.init = function() {
            var self = this;

            if (this.groups) {
                this.dropdown.change(function() {
                    self.onGroupChange();
                });
                this.onGroupChange();
            }
        };

        /**
         * Callback for when group changes.
         */
        this.onGroupChange = function() {
            var groupId = this.dropdown.val();
            var group = this.groups.hasOwnProperty(groupId) ? this.groups[groupId] : null;
            this.receiptField.onGroupChange(group);
        };

        this.init();
    };

    $(document).ready(function() {
        var receiptField = new ReceiptField();
        new GroupField(receiptField);
    });
})();
