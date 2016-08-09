(function() {
    'use strict';

    var Inventory = function() {
        this.element = $('#menus');
        this.menus = [];

        this.init = function() {
            var self = this;
            this.element.find('.menu').each(function(key, value) {
                self.menus.push(new Menu(self, $(value)));
            });

            holmes({
                input: '#menu-search',
                find: '.menu-item',
                class: {
                    visible: false,
                    hidden: 'hidden',
                },
                dynamic: true,
                instant: true,
                onHidden: function(element) {
                    self.getMenuItem($(element)).onHidden();
                },
                onVisible: function(element) {
                    self.getMenuItem($(element)).onVisible();
                }
            });
        };

        this.getMenuItem = function(element) {
            for(var i = 0; i < this.menus.length; i++) {
                var menu = this.menus[i];
                for(var j = 0; j < menu.items.length; j++) {
                    var item = menu.items[j];
                    if(item.element[0] == element[0])
                        return item;
                }
            }
            return null;
        };

        this.onHidden = function(item) {

        };

        this.onVisible = function(item) {
        };

        this.init();
    };

    var Menu = function(inventory, element) {
        this.inventory = inventory;
        this.element = element;
        this.items = [];
        this.hiddenItems = 0;

        this.init = function() {
            var self = this;
            this.element.find('.menu-item').each(function(key, value) {
                self.items.push(new MenuItem(self, $(value)));
            });
        };

        this.update = function() {
            if(this.hiddenItems >= this.items.length) {
                this.hide();
            } else {
                this.show();
            }
        };

        this.hide = function() {
            this.element.hide();
        };

        this.show = function() {
            this.element.show();
        };

        this.init();
    };

    var MenuItem = function(menu, element) {
        this.menu = menu;
        this.element = element;

        this.init = function() {

        };

        this.onVisible = function() {
            this.menu.hiddenItems--;
            this.menu.update();
        };

        this.onHidden = function() {
            this.menu.hiddenItems++;
            this.menu.update();
        };

        this.init();
    };

    $(document).ready(function() {
        new Inventory();
    });

})();
