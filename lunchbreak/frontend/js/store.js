(function() {
    'use strict';

    /**
     * Object returned on validation.
     * @typedef {Validation}
     * @type {object}
     * @property {bool} valid Whether the validation was successful or not.
     * @property {?string} errorMessage Message to be displayed an error occurred.
     */
    var Validation = function(message, valid) {
        this.errorMessage = message || null;
        if (message && valid === undefined) {
            // Valid defaults to false when there is a message set.
            // It can be overriden by providing valid in the constructor.
            this.valid = false;
        } else {
            // If no parameters are given, it defaults to true
            this.valid = true;
        }
    };

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
     * Get a formatted money string of the value given.
     * @param  {number} value Money value.
     * @return {string} Foramtted money string.
     */
    var moneyFilter = function(value) {
        return ('&euro; ' + Math.ceil10(value, -2).toFixed(2)).replace('.', ',');
    };


    /**
     * Get a representation for a value based on an inputtype.
     * @param  {FoodType.InputType} inputtype Input type of the value.
     * @param  {number} value Amount/weight value.
     * @return {string} Representation of the given value and input type.
     */
    var amountFilter = function(value, inputtype) {
        if (inputtype === FoodType.InputType.SIVariable) {
            return weightFilter(value);
        } else {
            return Math.round(value);
        }
    };

    /**
     * A weight representation of a value in kg or g.
     * @param  {number} value Weight in kg.
     * @return {string} SI unit representation.
     */
    var weightFilter = function(value) {
        if (value < 1)
            return (value * 1000) + ' g';
        else
            return String(value).replace('.', ',') + ' kg';
    };

    /**
     * Inventory representation that holds all menus.
     */
    var Inventory = function() {};

    /**
     * Load the menus and start initializing those together with holmes.js.
     */
    Inventory.init = function() {
        Inventory.element = $('#inventory');
        Inventory.menus = [];

        Inventory.element.find('.menu').each(function(key, value) {
            Inventory.menus.push(new Menu($(value)));
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
                Inventory.getFood($(element)).onHidden();
            },
            onVisible: function(element) {
                Inventory.getFood($(element)).onVisible();
            }
        });
    };

    /**
     * Get the Food instance from a Food element.
     * @param  {jQuery} element jQuery element of a Food.
     * @return {?Food} Food instance or null.
     */
    Inventory.getFood = function(element) {
        for (var i = 0; i < Inventory.menus.length; i++) {
            var menu = Inventory.menus[i];
            for (var j = 0; j < menu.items.length; j++) {
                var item = menu.items[j];
                if (item.element[0] == element[0])
                    return item;
            }
        }
        return null;
    };

    /**
     * Show a snackbar with a message.
     * @param  {string} message The message to be shown.
     */
    Inventory.showSnackbar = function(message) {
        var data = {
            'message': message
        };
        $('#snackbar')[0].MaterialSnackbar.showSnackbar(data);
    };

    /**
     * Representation of what is currently ordered in the order list.
     */
    var Order = function() {};
    Order.orderedfood = [];

    Order.init = function() {
        Order.element = $('#order');
        Order.itemsElement = $('#orderedfood-list');
        Order.submitButton = Order.element.find('input[type="submit"]').first();
    };

    /**
     * Add an orderedfood to the Order, render and update its price.
     * @param {OrderedFood} orderedfood Orderedfood.
     */
    Order.addOrderedFood = function(orderedfood) {
        Order.submitButton.attr('disabled', false);
        Order.orderedfood.push(orderedfood);
        this.renderOrderedFood(orderedfood);
        orderedfood.fetch();
    };

    /**
     * Remove an orderedfood from the order and update the Order total.
     * @param  {OrderedFood} orderedfood OrderedFood to be removed.
     */
    Order.removeOrderedFood = function(orderedfood) {
        var index = Order.orderedfood.indexOf(orderedfood);
        if (index != -1) {
            Order.orderedfood.splice(index, 1);
            Order.onCostUpdate();

            if (Order.orderedfood.length == 0) {
                Order.submitButton.attr('disabled', true);
            }
        }
    };

    /**
     * Render an orderedfood into the order list.
     * @param  {OrderedFood} orderedfood Orderedfood that needs to be rendered.
     */
    Order.renderOrderedFood = function(orderedfood) {
        if (this.itemsElement.hasClass('empty'))
            this.itemsElement.removeClass('empty');

        var index = this.orderedfood.indexOf(orderedfood);

        Order.itemsElement.prepend(
            nunjucks.render(
                'orderedfood.html', {
                    'deletable': true,
                    'orderedfood': orderedfood,
                    'index': index
                }
            )
        );

        var element = Order.itemsElement.find('.orderedfood').first();
        orderedfood.attachElement(element);
    };

    /**
     * Calculate and update the total cost of the order list.
     */
    Order.updateTotal = function() {
        var costElement = Order.itemsElement.find('.order-total .order-total-cost').first();
        var total = 0;

        for (var i in Order.orderedfood) {
            var orderedfood = Order.orderedfood[i];
            total += orderedfood.getTotal();
        }

        costElement.html(moneyFilter(total));
    };

    /**
     * Callback for when one of the orderedfood's cost updates.
     */
    Order.onCostUpdate = function() {
        Order.updateTotal();
    };

    /**
     * OrderedFood belonging to Order.
     * @param {Food} original Parent original.
     * @param {number} amount Amount of original selected.
     */
    var OrderedFood = function(original, amount) {
        this.original = original;
        this.amount = amount;

        /**
         * Get a formatted amount for use in the order list.
         * @return {string} Formatted amount.
         */
        this.amountFilter = function() {
            return amountFilter(this.amount, this.original.foodtype.inputtype);
        };

        /**
         * Calculate the total cost of the orderedfood based on the inputtype,
         * cost and amount of food. All rounded to 2 decimals.
         * @return {number} Total cost.
         */
        this.getTotal = function() {
            var amountFood = this.original.foodtype.inputtype === FoodType.InputType.SIAmount ? this.original.amount : 1;
            return Math.ceil10(this.cost * this.amount * amountFood, -2);
        };

        /**
         * Get the total cost displayed in an appropriate money format.
         * @return {string} Total cost formatted.
         */
        this.getTotalDisplay = function() {
            if (this.cost === undefined)
                return '...';
            return moneyFilter(this.getTotal());
        };

        /**
         * A JSON representation of the object passed onto the form and then
         * the backend.
         * @return {string} JSON representation
         */
        this.json = function() {
            var data = {
                'original': this.original.id,
                'amount': this.amount,
                'total': this.getTotal()
            };

            var selectedIngredientsIds = [];
            for (var i = 0; i < this.original.ingredients.length; i++) {
                var ingredient = this.original.ingredients[i];
                if (ingredient.selected)
                    selectedIngredientsIds.push(ingredient.id);
            }

            if (selectedIngredientsIds.length > 0)
                data['ingredients'] = selectedIngredientsIds;

            var json = JSON.stringify(data);

            return json;
        };

        /**
         * Update the properties with the JSON data.
         * @param  {Object.<string, object>} json JSON data.
         * @param {bool} force Force an update.
         * (Interface, doesn't do anything here)
         */
        this.update = function(cost, force) {
            this.cost = cost;
            this.updateCost();
        };

        /**
         * Update the cost displayed in the order list. Will also update the
         * total cost of the order list.
         */
        this.updateCost = function() {
            var costElement = this.element.find('.orderedfood-cost').first();
            costElement.html(this.getTotalDisplay());
            this.element.find('.orderedfood-data').first().val(this.json());

            Order.onCostUpdate();
        };

        /**
         * Update the price of the orderedfood by fetching it from the
         * Lunchbreak API and update the object.
         */
        this.fetch = function() {
            var self = this;

            OrderedFood.fetchCost(this.original, function(cost) {
                self.update(cost);
            });
        };

        /**
         * Attach an element to the orderedfood.
         * @param  {jQuery} element jQuery element.
         */
        this.attachElement = function(element) {
            this.element = element;

            var self = this;
            this.element.find('.orderedfood-cost').on('click', function(event) {
                self.onDelete();
            });
        };

        /**
         * Delete the OrderedFood from the list of orders.
         */
        this.onDelete = function() {
            this.element.remove();
            Order.removeOrderedFood(this);
        };
    };

    /**
     * Get the updated price from the API.
     * @param  {Food} food Base food.
     * @param  {Function} callback Callback function with cost.
     */
    OrderedFood.fetchCost = function(food, callback) {
        var ingredientIds = [];

        for (var i in food.ingredients) {
            var ingredient = food.ingredients[i];
            if (ingredient.selected)
                ingredientIds.push(ingredient.id);
        }

        var data = [{
            original: food.id,
            ingredients: ingredientIds
        }];

        $.ajax({
            type: 'POST',
            data: JSON.stringify(data),
            url: '/api/customers/order/price/',
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(json) {
                callback(json[0]['cost']);
            },
            failure: function(data) {
                Inventory.showSnackbar('Er trad een fout op bij het vernieuwen van de prijs.');
            }
        });
    };

    /**
     * A menu in the inventory, holds a list of foods.
     * @param {jQuery} element jQuery element.
     */
    var Menu = function(element) {
        this.element = element;
        this.items = [];
        this.hiddenItems = 0;

        /**
         * Initialize the food in the menu.
         */
        this.init = function() {
            var self = this;
            this.element.find('.food').each(function(key, value) {
                self.items.push(new Food(self, $(value)));
            });
        };

        this.updateVisibility = function() {
            if (this.hiddenItems >= this.items.length)
                this.element.hide();
            else
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
        this.addButton = this.element.find('.food-add');
        this.confirmButtonSelector = '.food-confirm';
        this.labelSelector = '.food-amount label';
        this.updated = false;
        this.rendered = false;
        this.json = null;

        this.id = this.element.data('id');
        this.hasIngredients = this.element.data('has-ingredients') === 'True';

        /**
         * Get a representation of the cost.
         * @return {string} Example: "&euro; 3,50".
         */
        this.getCostDisplay = function() {
            var simpleQuantifier = this.foodtype.inputtype === FoodType.InputType.SIVariable ? 'kg' : 'stuk';
            return moneyFilter(this.cost) + ' / ' + simpleQuantifier;
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
         * Get the amount used for input.
         * Weights are represented as decimals, but inputted as times e3.
         * @return {integer} Amount used for data input.
         */
        this.getIntegerAmount = function() {
            if (this.foodtype.inputtype === FoodType.InputType.SIVariable) {
                return this.amount * 1000;
            }

            return this.amount;
        };

        /**
         * Get amount in decimal form from the input field.
         * @return {decimal} Amount in decimal form.
         */
        this.getDecimalAmount = function() {
            var amount = parseInt(this.inputField.val());

            if (this.foodtype.inputtype === FoodType.InputType.SIVariable) {
                amount /= 1000;
            }

            return amount;
        };

        /**
         * Get the selected ingredient groups of the food.
         * @return {IngredientGroup[]} List of ingredient groups
         */
        this.getSelectedIngredientGroups = function() {
            var selectedGroups = [];
            for (var i in this.ingredientgroups) {
                var group = this.ingredientgroups[i];
                if (group.isSelected())
                    selectedGroups.push(group);
            }
            return selectedGroups;
        };

        /**
         * Initialize all element events.
         */
        this.init = function() {
            var self = this;
            this.addButton.on('click', function() {
                self.onAdd();
            });
            this.element.on('click', '.food-cancel', function() {
                self.toggle();
            });
            this.element.on(
                'click',
                '.ingredientgroup-more',
                IngredientGroup.onExpandIngredients
            );
            this.element.on(
                'click',
                this.confirmButtonSelector,
                function() {
                    self.onConfirm();
                }
            );
        };

        /**
         * Add selected Food and ingredients to order.
         * Call reset after doing so.
         */
        this.addToOrder = function() {
            var clone = jQuery.extend(true, {}, this);
            var orderedfood = new OrderedFood(clone, this.getDecimalAmount());
            this.reset();
            Order.addOrderedFood(orderedfood);
        };

        /**
         * Reset the food back to its original content.
         */
        this.reset = function() {
            if (this.json) {
                this.update(this.json, true);
                this.render(true)
            }
            this.inputField.parent()[0].MaterialTextfield.change(this.getIntegerAmount());
        };

        /**
         * Toggle the expanding of the Food element.
         */
        this.toggle = function() {
            if (this.element.hasClass('expanded'))  {
                this.element.removeClass('expanded');
            } else {
                this.element.addClass('expanded');
                if (this.json)
                    this.reset();
            }
        };

        /**
         * Retrieve detailed info of the object from the Lunchbreak API.
         * Afterwards call `update` and `render` the Food.
         */
        this.fetch = function() {
            if (!this.json) {
                var self = this;
                $.getJSON(
                    '/api/customers/food/' + this.id + '/',
                    function(json) {
                        self.update(json);
                        self.render();
                    }
                );
            }
        };

        /**
         * Update the properties with the JSON data. Also add Food.ingredients
         *  to the associated Food.ingredientgroups.
         * @param  {Object.<string, object>} json JSON data.
         * @param {bool} force Force an update.
         */
        this.update = function(json, force) {
            if (this.updated && !force)
                return;

            this.json = json;

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
                    },
                    'quantity': {
                        class: Quantity
                    },
                    'foodtype': {
                        class: FoodType
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
         * Render the Food with a template into Food.element.
         */
        this.render = function(force) {
            if (this.rendered && !force)
                return;

            this.element.find('.food-top .food-text .food-form').remove();
            if (!this.foodFormRender)
                this.foodFormRender = nunjucks.render(
                    'food_form.html', {
                        'label': this.foodtype.getLabelDisplay(),
                        'food': this
                    }
                );
            this.element.find('.food-top .food-text').append(this.foodFormRender);

            if (this.hasIngredients) {
                this.element.find('.ingredientgroups').remove();
                if (!this.ingredientGroupsRender)
                    this.ingredientGroupsRender = nunjucks.render(
                        'ingredient_groups.html', {
                            'food': this
                        }
                    );
                this.element.append(this.ingredientGroupsRender);

                var ingredientgroupsElement = this.element.find('.ingredientgroups');

                ingredientgroupsElement.find('table, thead, tbody, tfoot, colgroup, caption, label, legend, script, style, textarea, button, object, embed, tr, th, td, li, h1, h2, h3, h4, h5, h6, form, .ingredientgroup').addClass('dontsplit');
                ingredientgroupsElement.find('h1, h2, h3, h4, h5, h6').addClass('dontend');
                ingredientgroupsElement.find('br').addClass('removeiflast').addClass('removeiffirst');
                ingredientgroupsElement.columnize({
                    'columns': 2,
                    'buildOnce': false,
                    'lastNeverTallest': true
                });

                var self = this;
                this.element.find('.ingredientgroups .ingredientgroup').each(function(index) {
                    var ingredientgroup = self.ingredientgroups[index];
                    ingredientgroup.attachElement($(this));
                });

            }

            componentHandler.upgradeAllRegistered();

            var self = this;
            this.inputField = this.element.find('.food-amount input').first();
            this.inputField.on('keyup', function(event) {
                self.onInputChange();
            });
            this.inputError = this.element.find('.food-amount .mdl-textfield__error').first();

            this.rendered = true;
        };

        /**
         * Validate whether the selected amount is adhering to the rules.
         * @return {Validation}
         */
        this.validate = function() {
            var value = this.getDecimalAmount();
            if (value === NaN)
                return new Validation(
                    'Gelieve een geldig nummer in te geven.'
                );

            if (this.foodtype.inputtype !== FoodType.InputType.SIVariable) {
                if (value % 1 != 0) {
                    // The value is a decimal
                    return new Validation(
                        'Moet een geheel getal zijn.'
                    );
                }
            }

            if (this.quantity !== null) {
                if (value < this.quantity.minimum) {
                    return new Validation(
                        'Minimum ' + this.quantity.getMinimumDisplay() + '.'
                    );
                } else if (value > this.quantity.maximum) {
                    return new Validation(
                        'Maximum ' + this.quantity.getMaximumDisplay() + '.'
                    );
                }
            }
            return new Validation();
        };

        this.fetchCost = function() {
            var self = this;

            OrderedFood.fetchCost(this, function(cost) {
                self.cost = cost;
                self.onCostChange();
            });
        };

        /**
         * Holmes onChange callback for showing items.
         */
        this.onVisible = function() {
            this.menu.hiddenItems--;
            this.menu.updateVisibility();
        };

        /**
         * Holmes onChange callback for hiding items.
         */
        this.onHidden = function() {
            this.menu.hiddenItems++;
            this.menu.updateVisibility();
        };

        /**
         * Callback when clicking the add button.
         */
        this.onAdd = function() {
            this.toggle();
            this.fetch();
        };

        /**
         * Set the error message of the amount input field.
         * @param {string} message Message.
         */
        this.setInputError = function(message) {
            if (message === '') {
                this.inputError.text(this.originalErrorMessage);
            } else {
                if (this.originalErrorMessage === undefined)
                    this.originalErrorMessage = this.inputError.text();

                if (this.inputError.text() !== message) {
                    this.inputError.text(message);
                }
                this.inputError.parent().addClass('is-focused');
                this.inputError.parent().addClass('is-invalid');
            }
        };

        /**
         * Callback for input field when value changes.
         */
        this.onInputChange = function() {
            if (this.inputField.val() !== '') {
                var validation = this.validate();
                if (!validation.valid) {
                    this.setInputError(validation.errorMessage);
                    return;
                }
            }
            this.setInputError('');
        };

        /**
         * Callback when confirming to add it to the order.
         */
        this.onConfirm = function() {
            var validation = this.validate();
            if (validation.valid) {
                this.addToOrder();
                this.setInputError('');
                this.toggle();
            } else {
                this.setInputError(validation.errorMessage);
            }
        };

        /**
         * Callback when the cost changes.
         * @return {[type]} [description]
         */
        this.onCostChange = function() {
            this.element
                .find(this.labelSelector)
                .html(this.foodtype.getLabelDisplay() + ' (' + this.getCostDisplay() + ')');
        };

        this.init();
    };

    /**
     * FoodType of a food.
     * @param {Food} food Parent food.
     * @param {Object.<string, object>} json JSON data.
     */
    var FoodType = function(food, json) {
        this.food = food;

        /**
         * Get a label used for inputting a value for the food.
         * @return {string} Label for input field.
         */
        this.getLabelDisplay = function() {
            switch (this.inputtype) {
                case FoodType.InputType.Amount:
                    return 'Hoeveelheid';
                    break;
                case FoodType.InputType.SIVariable:
                    return 'Gewicht (g)';
                    break;
                case FoodType.InputType.SIAmount:
                    var inputtype = this.inputtype === FoodType.InputType.Amount ? this.inputtype : FoodType.InputType.SIVariable;
                    return 'Aantal (elk ' + amountFilter(this.food.amount, inputtype) + ')';
                    break;
            }
        };

        /**
         * Update the foodtype on initialization.
         */
        this.init = function() {
            this.update(json);
        };

        /**
         * Update the properties with the JSON data.
         * @param  {Object.<string, object>} json JSON data.
         * @param {bool} force Force an update.
         */
        this.update = function(json, force) {
            if (this.updated && !force)
                return;

            mapJson({},
                this,
                json
            );

            this.updated = true;
        };

        this.init();
    };

    /**
     * FoodType InputType 'enum'.
     * @type {object}
     */
    FoodType.InputType = {
        Amount: 0,
        SIVariable: 1,
        SIAmount: 2
    };

    /**
     * Quantity of a food.
     * @param {Food} food Parent food.
     * @param {Object.<string, object>} json JSON data.
     */
    var Quantity = function(food, json) {
        this.food = food;

        this.getMinimumDisplay = function() {
            return amountFilter(
                this.minimum,
                this.food.foodtype.inputtype
            );
        };

        this.getMaximumDisplay = function() {
            return amountFilter(
                this.maximum,
                this.food.foodtype.inputtype
            );
        };

        this.init = function() {
            this.update(json);
        };

        /**
         * Update the properties with the JSON data.
         * @param  {Object.<string, object>} json JSON data.
         * @param {bool} force Force an update.
         */
        this.update = function(json, force) {
            if (this.updated && !force)
                return;

            mapJson({},
                this,
                json
            );

            this.updated = true;
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
         * @param {bool} force Force an update.
         */
        this.update = function(json, force) {
            if (this.updated && !force)
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
         * Validate whether the selected ingredients are adhering to the rules.
         * @return {Validation}
         */
        this.validate = function() {
            if (this.minimum === 0 && this.maximum === 0)
                return Validation();

            var selectedIngredients = this.getSelectedIngredients();

            var selectedAmount = selectedIngredients.length;
            if (selectedAmount < this.minimum) {
                return new Validation(
                    'Gelieve er minimum ' + this.minimum + ' te selecteren.'
                );
            } else if (selectedAmount > this.maximum) {
                return new Validation(
                    'Gelieve er maximum ' + this.maximum + ' te selecteren.'
                );
            }
            return new Validation();
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

        /**
         * If there are ingredients selected in this ingredient group,
         * then this ingredient group is selected.
         * @return {Boolean} Whether this group is selected.
         */
        this.isSelected = function() {
            return this.getSelectedIngredients().length > 0;
        };

        this.init();
    };

    /**
     * The different ingredient group calculations.
     * @type {Object.<integer>}
     */
    IngredientGroup.Calculations = {
        ALWAYS: 0,
        ADDITIONS: 1,
        BOTH: 2
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
         * @param {bool} force Force an update.
         */
        this.update = function(json, force) {
            if (this.updated && !force)
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

            // Do not modify the json, needed for restoration
            json.ingredient = ingredient;
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
        this.onToggle = function(event) {
            if (this.selected)
                this.deselect();
            else
                this.select();
            var wasSelected = this.selected;
            var validation = this.group.validate();
            if (!validation.valid)  {
                if (this.group.maximum === 1) {
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
                } else {
                    Inventory.showSnackbar(validation.errorMessage);
                    this.deselect();
                }
            }

            // If the toggle was reverted, don't change anything.
            if (wasSelected != this.selected)
                return;

            this.onSelectedChange();
        };

        /**
         * Callback for when selected changes.
         * Changes the cost based on the ingredient price, not the group price.
         */
        this.onSelectedChange = function() {
            this.food.fetchCost();
        };

        /**
         * Attach an element to the ingredient.
         * @param  {jQuery} element jQuery element.
         */
        this.attachElement = function(element) {
            this.element = element;

            var self = this;
            this.element.change(function(event) {
                self.onToggle(event);
            });
        };

        this.init();
    };

    /**
     * Representation of the tab container on the website.
     */
    var TabContainer = function() {
        this.element = $('#menu-tabs');
        this.header = $('#header');
        this.storeInfo = $('#store-info');
        this.stickyClass = 'sticky';

        this.init = function() {
            this.position = this.element.position();
            this.onPositionChange();
            this.tabs = [];

            var self = this;

            this.element.find('ul li').each(function() {
                self.tabs.push(
                    new Tab(self, $(this))
                );
            });
            $(window).resize(function(event) {
                self.onPositionChange(event);
            });
            $(window).scroll(function(event) {
                self.onPositionChange(event);
            });
            $(window).on('wheel DOMMouseScroll mousesheel keyup touchmove', function(event) {
                // Stop the tab scrolling animation if the user interacts with the page
                $('html, body').stop();
            });
        };

        /**
         * Callback triggered for when the position of the tab container might change.
         * @param  {Event} event Event that caused this change.
         */
        this.onPositionChange = function(event) {
            var scrollTop = $(document).scrollTop();
            var headerHeight = this.header.height();

            var relativePosition = this.position.top - headerHeight;
            var difference = relativePosition - scrollTop;
            var percentage = Math.max(difference / relativePosition, 0);

            var storeInfoBackground = 'rgba(255, 255, 255, ' + (1 - percentage) + ')';
            var storeInfoColor = 'rgba(255, 255, 255, ' + percentage + ')';
            var whiteColor = $.Color('rgb(255, 255, 255)');
            var darkGreyColor = $.Color('rgb(76, 76, 76)');

            var fadeTime = 50;
            this.storeInfo.stop();
            this.storeInfo.animate({
                backgroundColor: storeInfoBackground,
                color: storeInfoColor
            }, fadeTime);
            this.header.animate({
                color: whiteColor.transition(darkGreyColor, 1 - percentage)
            }, fadeTime);
            Order.element.css('width', Order.element.width());

            if (difference <= 0) {
                this.element.addClass(this.stickyClass);
                this.header.addClass(this.stickyClass);
                this.header.addClass('white');
                Order.element.addClass(this.stickyClass);

                Inventory.element.css('margin-top', this.element.height() + 'px');
                Order.element.css('margin-top', (this.header.height() + this.element.height()) + 'px');
            } else {
                this.element.removeClass(this.stickyClass);
                this.header.removeClass(this.stickyClass);
                this.header.removeClass('white');
                Order.element.removeClass(this.stickyClass);
                Inventory.element.css('margin-top', '0px');
                Order.element.css('margin-top', '0px');
            }
        };

        this.init();
    };

    /**
     * Representation of a tab in the tab container.
     * @param {TabContainer} container Parent tab container.
     * @param {jQuery} element jQuery element.
     */
    var Tab = function(container, element) {
        this.container = container;
        this.element = element;

        this.init = function() {
            var self = this;

            this.element.on('click', function(event) {
                self.onClick(event);
            });
        };

        /**
         * Callback for when the tab is clicked.
         * @param  {Event} event Click event.
         */
        this.onClick = function(event) {
            var menuId = this.element.data('id');
            var menuElement = $('.menu[data-id="' + menuId + '"]').first();

            $.each(this.container.tabs, function(index) {
                this.element.removeClass('selected');
            });
            this.element.addClass('selected');

            // Scroll to the selected item
            var fullHeaderHeight = this.container.element.height() + this.container.header.height();
            var scrollTop = menuElement.offset().top - fullHeaderHeight - 16;
            $('html, body').stop();
            $('html, body').animate({
                'scrollTop': scrollTop
            }, 1000);
        };

        this.init();
    };

    $(document).ready(function() {
        var env = nunjucks.configure('/static', {
            autoescape: true
        });
        env.addFilter('amount', amountFilter);
        env.addFilter('money', moneyFilter);

        Order.init();
        Inventory.init();
        new TabContainer();
    });

})();
