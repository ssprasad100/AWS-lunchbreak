(function() {
    'use strict';


    var map_json = function(mapping, instance, json) {
        for(var key in json) {
            var value = json[key];
            if(mapping.hasOwnProperty(key)) {
                var mapInfo = mapping[key];
                if(mapInfo.hasOwnProperty('key'))
                    key = mapInfo.key;
                if(mapInfo.hasOwnProperty('class')) {
                    if(Array.isArray(value)) {
                        var result = [];
                        for(var i in value)
                            result.push(new mapInfo.class(instance, value[i]));
                        instance[key] = result;
                        continue;
                    } else {
                        instance[key] = new mapInfo.class(instance, value);
                        continue;
                    }
                }
            }
            instance[key] = value;
        }
    };

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
                find: '.food',
                class: {
                    visible: false,
                    hidden: 'hidden',
                },
                dynamic: true,
                instant: true,
                onHidden: function(element) {
                    self.getFood($(element)).onHidden();
                },
                onVisible: function(element) {
                    self.getFood($(element)).onVisible();
                }
            });
        };

        this.getFood = function(element) {
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

        this.init();
    };

    var Menu = function(inventory, element) {
        this.inventory = inventory;
        this.element = element;
        this.items = [];
        this.hiddenItems = 0;

        this.init = function() {
            var self = this;
            this.element.find('.food').each(function(key, value) {
                self.items.push(new Food(self, $(value)));
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

    var Food = function(menu, element) {
        this.menu = menu;
        this.element = element;
        this.expanded = false;
        this.addButton = element.find('.food-add');
        this.updated = false;

        this.id = this.element.data('id');
        this.hasIngredients = this.element.data('has-ingredients') === 'True';


        this.init = function() {
            var self = this;
            this.addButton.on('click', function() {
                self.onAdd();
            });
        };

        this.onVisible = function() {
            this.menu.hiddenItems--;
            this.menu.update();
        };

        this.onHidden = function() {
            this.menu.hiddenItems++;
            this.menu.update();
        };

        this.render = function() {
            var foodFormTemplate = $.templates('#templateFoodForm');
            this.element.find('.food-top .food-text').append(
                foodFormTemplate.render({
                    label: 'Gewicht (kg)',
                    food: this
                })
            );

            var ingredientGroupsTemplate = $.templates('#templateIngredientGroups');
            this.element.append(
                ingredientGroupsTemplate.render({
                    food: this
                })
            );
            componentHandler.upgradeAllRegistered();
        };

        this.toggle = function() {
            if(this.expanded)
                this.element.removeClass('expanded');
            else {
                this.element.addClass('expanded');
            }
        };

        this.getIngredientGroup = function(id) {
            for(var i = 0; i < this.ingredientgroups.length; i++) {
                var ingredientgroup = this.ingredientgroups[i];
                if(ingredientgroup.id == id)
                    return ingredientgroup;
            }
            return null;
        };

        this.update = function(json) {
            map_json(
                {
                    'has_ingredients': {
                        key: 'hasIngredients'
                    },
                    'last_modified': {
                        key: 'lastModified'
                    },
                    'preorder_days': {
                        key: 'preorderDays'
                    },
                    'ingredients': {
                        class: Ingredient
                    },
                    'ingredientgroups': {
                        class: IngredientGroup
                    }
                },
                this,
                json
            );

            for(var i in this.ingredients) {
                var ingredient = this.ingredients[i];
                var ingredientgroup = this.getIngredientGroup(ingredient.group);
                console.log(ingredientgroup);
                if(ingredientgroup.ingredients === undefined)
                    ingredientgroup.ingredients = [ingredient];
                else
                    ingredientgroup.ingredients.push(
                        ingredient
                    );
            }

            this.updated = true;
        };

        this.fetch = function() {
            if(this.updated)
                return;

            var self = this;
            $.getJSON(
                '/api/customers/food/' + this.id + '/', function(json) {
                    self.update(json);
                    self.render();
                }
            );
        };

        this.onAdd = function() {
            if(this.hasIngredients) {
                this.toggle();
                this.fetch();
            } else {
                alert('Directly adding to order, no ingredients.');
            }
        };

        this.init();
    };

    var IngredientGroup = function(food, json) {
        this.food = food;
        this.updated = false;

        this.init = function() {
            this.update(json);
        };

        this.update = function(json) {
            if(this.updated)
                return;

            map_json(
                {},
                this,
                json
            )
            this.updated = true;
        };

        this.init();
    };

    var Ingredient = function(food, json) {
        this.food = food;
        this.updated = false;

        this.init = function() {
            this.update(json);
        };

        this.update = function(json) {
            if(this.updated)
                return;

            var ingredient = json.ingredient;
            json.ingredient = undefined;

            // Will 'currently' only contain selected for the ingredient relation
            map_json(
                {},
                this,
                json
            )

            // This is the real info
            map_json(
                {},
                this,
                ingredient
            )
            this.updated = true;
        };

        this.init();
    };

    $(document).ready(function() {
        new Inventory();
    });

})();
