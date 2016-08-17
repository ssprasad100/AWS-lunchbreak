(function() {
    'use strict';

    /**
     * Map json keys and values to instance properties.
     * @param  {Object.<string, Object.<string, object>>} mapping Mapping settings.
     * @param  {object} instance Instance where to set the properties on.
     * @param  {Object.<string, object>} json JSON data.
     */
    var mapJson = function(mapping, instance, json) {
        for (var key in json) {
            var value = json[key];
            if (mapping.hasOwnProperty(key))  {
                var mapInfo = mapping[key];
                if (mapInfo.hasOwnProperty('key'))
                    key = mapInfo.key;
                if (mapInfo.hasOwnProperty('class')) {
                    if (Array.isArray(value)) {
                        var result = [];
                        for (var i in value)
                            result.push(
                                new mapInfo.class(instance, value[i])
                            );
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

    /**
     * Inventory representation that holds all menus.
     */
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
                find: '.food:not(.expanded)',
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

        /**
         * Get the Food instance from a Food element.
         * @param  {jQuery} element jQuery element of a Food.
         * @return {?Food} Food instance or null.
         */
        this.getFood = function(element) {
            for (var i = 0; i < this.menus.length; i++) {
                var menu = this.menus[i];
                for (var j = 0; j < menu.items.length; j++) {
                    var item = menu.items[j];
                    if (item.element[0] == element[0])
                        return item;
                }
            }
            return null;
        };

        this.init();
    };

    /**
     * Show a snackbar with a message.
     * @param  {strign} message The message to be shown.
     */
    Inventory.showSnackbar = function(message) {
        var data = {
            'message': message
        };
        $('#snackbar')[0].MaterialSnackbar.showSnackbar(data);
    };

    /**
     * A menu in the inventory, holds a list of foods.
     * @param {Inventory} inventory Parent inventory.
     * @param {jQuery} element jQuery element.
     */
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
            if (this.hiddenItems >= this.items.length)  {
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

    /**
     * Food belonging to a menu.
     * @param {Menu} menu Parent menu.
     * @param {jQuery} element jQuery element.
     */
    var Food = function(menu, element) {
        this.menu = menu;
        this.element = element;
        this.addButton = element.find('.food-add');
        this.updated = false;

        this.id = this.element.data('id');
        this.hasIngredients = this.element.data('has-ingredients') === 'True';

        this.init = function() {
            var self = this;
            this.addButton.on('click', function() {
                self.onAdd();
            });
            this.element.on('click', '.food-cancel', function() {
                self.toggle();
            });
            this.element.on('click', '.ingredientgroup-more', IngredientGroup.onExpandIngredients);
        };

        /**
         * Get a representation of the cost.
         * @return {string} Example: "&euro; 3,50".
         */
        this.getCostDisplay = function() {
            return '&euro; ' + this.cost.toFixed(2).replace('.', ',');
        };

        /**
         * Holmes onChange callback for showing items.
         */
        this.onVisible = function() {
            this.menu.hiddenItems--;
            this.menu.update();
        };

        /**
         * Holmes onChange callback for hiding items.
         */
        this.onHidden = function() {
            this.menu.hiddenItems++;
            this.menu.update();
        };

        /**
         * Render the Food with a JsRender template into Food.element.
         */
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

            var self = this;
            this.element.find('.ingredientgroups .ingredientgroup').each(function(index) {
                var ingredientgroup = self.ingredientgroups[index];
                ingredientgroup.attachElement($(this));
            });
        };

        /**
         * Toggle the expanding of the Food element.
         */
        this.toggle = function() {
            if (this.element.hasClass('expanded'))
                this.element.removeClass('expanded');
            else
                this.element.addClass('expanded');
        };

        /**
         * Get an IngredientGroup instance based on its id.
         * @param  {integer} id IngredientGroup id.
         * @return {?IngredientGroup} Associated IngredientGroup.
         */
        this.getIngredientGroup = function(id) {
            for (var i = 0; i < this.ingredientgroups.length; i++) {
                var ingredientgroup = this.ingredientgroups[i];
                if (ingredientgroup.id == id)
                    return ingredientgroup;
            }
            return null;
        };

        /**
         * Update the properties with the JSON data. Also add Food.ingredients
         *  to the associated Food.ingredientgroups.
         * @param  {Object.<string, object>} json JSON data.
         */
        this.update = function(json) {
            mapJson({
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

            for (var i in this.ingredients) {
                var ingredient = this.ingredients[i];
                var ingredientgroup = this.getIngredientGroup(ingredient.group);
                if (ingredientgroup.ingredients === undefined)
                    ingredientgroup.ingredients = [ingredient];
                else
                    ingredientgroup.ingredients.push(
                        ingredient
                    );
                ingredient.group = ingredientgroup;
            }

            this.updated = true;
        };

        /**
         * Retrieve detailed info of the object from the Lunchbreak API.
         * Afterwards call `update` and `render` the Food.
         */
        this.fetch = function() {
            if (this.updated)
                return;

            var self = this;
            $.getJSON(
                '/api/customers/food/' + this.id + '/',
                function(json) {
                    self.update(json);
                    self.render();
                }
            );
        };

        /**
         * Callback when clicking the add button.
         */
        this.onAdd = function() {
            if (this.hasIngredients) {
                this.toggle();
                this.fetch();
            } else {
                Inventory.showSnackbar('Toegevoegd aan bestelling.');
            }
        };

        this.init();
    };

    /**
     * IngredientGroup of a food.
     * @param {Food} food Parent food.
     * @param {Object.<string, object>} json JSON data.
     */
    var IngredientGroup = function(food, json) {
        this.food = food;
        this.updated = false;

        this.init = function() {
            this.update(json);
        };

        /**
         * Update the properties with the JSON data.
         * @param  {Object.<string, object>} json JSON data.
         */
        this.update = function(json) {
            if (this.updated)
                return;

            mapJson({},
                this,
                json
            );

            if (this.maximum <= 0)
                this.maximum = Infinity;

            this.updated = true;
        };

        /**
         * Attach an element to the IngredientGroup.
         * Recursively attaches the elements for the group's ingredients.
         * @param  {jQuery} element jQuery element.
         */
        this.attachElement = function(element) {
            this.element = element;

            var self = this;
            this.element.find('.ingredient').each(function(index) {
                var ingredient = self.ingredients[index];
                ingredient.attachElement($(this));
            });
        };

        /**
         * Object returned on validation.
         * @typedef {Validation}
         * @type {object}
         * @property {bool} valid Whether the validation was successful or not.
         * @property {?string} errorMessage Message to be displayed an error occurred.
         */

        /**
         * Validate whether the selected ingredients are adhering to the rules.
         * @return {validation}
         */
        this.validate = function() {
            var validation = {
                valid: true,
                errorMessage: null
            };
            if (this.minimum === 0 && this.maximum === 0)
                return validation;

            var selectedIngredients = this.getSelectedIngredients();

            var selectedAmount = selectedIngredients.length;
            if (selectedAmount < this.minimum) {
                validation['valid'] = false;
                validation['errorMessage'] = 'Gelieve er minimum ' + this.minimum + ' te selecteren.';
            } else if (selectedAmount > this.maximum) {
                validation['valid'] = false;
                validation['errorMessage'] = 'Gelieve er maximum ' + this.maximum + ' te selecteren.';
            }
            return validation;
        };

        /**
         * Get the selected ingredients of the IngredientGroup.
         * @return {Ingredient[]} List of selected ingredients.
         */
        this.getSelectedIngredients = function() {
            var selectedIngredients = [];
            for (var i in this.ingredients) {
                var ingredient = this.ingredients[i];
                if (ingredient.selected)
                    selectedIngredients.push(ingredient);
            }
            return selectedIngredients;
        };

        this.init();
    };

    /**
     * Callback for when clicking 'Show all ingredients'.
     * @param  {Event} event Event instance.
     */
    IngredientGroup.onExpandIngredients = function(event) {
        var element = $(this);
        element.parent().find('.ingredient.hidden').each(function(index) {
            $(this).removeClass('hidden');
        });
    };

    /**
     * Ingredient of a food.
     * @param {Food} food Parent food.
     * @param {Object.<string, object>} json JSON data.
     */
    var Ingredient = function(food, json) {
        this.food = food;
        this.updated = false;

        this.init = function() {
            this.update(json);
        };

        /**
         * Update the properties with the JSON data. Also merge the
         * IngredientRelation and Ingredient into 1 Ingredient.
         * @param  {Object.<string, object>} json JSON data.
         */
        this.update = function(json) {
            if (this.updated)
                return;

            var ingredient = json.ingredient;
            json.ingredient = undefined;

            // Will 'currently' only contain selected for the ingredient relation
            mapJson({},
                this,
                json
            );

            // This is the real info
            mapJson({},
                this,
                ingredient
            );
            this.updated = true;
        };

        /**
         * Select the ingredient by setting Ingredient.selected and checking
         * the checkbox.
         */
        this.select = function() {
            this.selected = true;
            this.element.addClass('is-checked');
        };

        /**
         * Deselect the ingredient by setting Ingredient.selected and
         * unchecking the checkbox.
         */
        this.deselect = function() {
            this.selected = false;
            this.element.removeClass('is-checked');
        };

        /**
         * Callback when toggling the ingredient checkbox.
         */
        this.onToggle = function() {
            this.selected = this.element.hasClass('is-checked');
            var validation = this.group.validate();
            if (!validation.valid)  {
                if (this.group.minimum === 1 && this.group.maximum === 1) {

                    if (!this.selected) {
                        this.select();
                    } else {
                        var selectedIngredients = this.group.getSelectedIngredients();
                        for (var i in selectedIngredients) {
                            var ingredient = selectedIngredients[i];
                            if (this.id !== ingredient.id) {
                                ingredient.deselect();
                                break;
                            }
                        }
                    }
                    Inventory.showSnackbar(validation.errorMessage);
                } else {
                    Inventory.showSnackbar(validation.errorMessage);
                    this.deselect();
                }
            }
        };

        /**
         * Attach an element to the IngredientGroup.
         * Recursively attaches the elements for the group's ingredients.
         * @param  {jQuery} element jQuery element.
         */
        this.attachElement = function(element) {
            this.element = element;

            var self = this;
            this.element.change(function() {
                self.onToggle();
            });
        };

        this.init();
    };

    $(document).ready(function() {
        new Inventory();
    });

})();
