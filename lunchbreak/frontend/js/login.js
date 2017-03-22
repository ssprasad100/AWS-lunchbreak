(function() {

    var pager;
    var messages = {
        'timeout': 'Kon geen verbinding leggen met de server. Gelieve je internetverbinding te controleren en opnieuw te proberen.',
        'pin-request': 'PIN-code wordt aangevraagd...',
        'pin-sent': 'Code opnieuw verzonden!',
        'error-general': 'Er trad een fout op, gelieve opnieuw te proberen.',
        'namefield-subscript': 'Nooit meer je naam verkeerd geschreven op een kop koffie!',
        'errors': {
            130: 'Lunchbreak is tijdelijk overbelast, we zijn te populair!',
            235: 'PIN-code vervallen.',
            236: 'Foute PIN-code.',
            240: 'Niet '
        }
    };

    var getErrorMessage = function(request) {
        if (request.responseJSON !== undefined) {
            var json = request.responseJSON;
            if (json.error !== undefined && json.error.code !== undefined && messages['errors'].hasOwnProperty(json.error.code)) {
                return messages['errors'][json.error.code];
            }
        }
        return messages['error-general'];
    };

    var Pager = function(items) {
        this.items = items;
        this.position = 0;
        this.confirmButton = $("#login-confirm");
        this.pagerData = $('#pager-data');
        this.pagerTransition = $('#pager-transition');
        this.allowed = true;
        this.subscript = $('#login .subscript').first();
        this.data = {};

        this.init = function() {
            for (var i = 0; i < this.items.length; i++) {
                var item = this.items[i];

                var itemSelector = item['selector'];
                var itemElement = $(itemSelector);
                var itemClass = item['class'];

                itemClass.selector = itemSelector;
                itemClass.html = itemElement[0].outerHTML;
                itemClass.position = i;
            }
            this.pagerData.remove();

            this.page = new this.items[0]['class']();

            var self = this;
            this.confirmButton.on('click', function(event) {
                return self.onConfirm();
            });
            this.pagerTransition.on('keyup', 'input', function(event) {
                self.onChange();
            });
        };

        this.getInputField = function() {
            return this.confirmButton.prev().children().first();
        };

        this.setEnabled = function(inputfield, button, force) {
            if (!this.allowed && !force)
                return;

            this.confirmButton.attr(
                'disabled', !button
            );

            this.getInputField().attr(
                'disabled', !(inputfield === undefined ? true : inputfield)
            );
        };

        this.onConfirm = function() {
            var cancelEvent = this.page.onConfirm();

            return cancelEvent === true;
        };

        this.onChange = function() {
            this.page.onChange();
        };

        this.switchPage = function(position) {
            if (this.position == position)
                return;

            this.setEnabled(false, false);

            var item = this.items[position];
            var itemClass = item['class'];
            var inputfield = this.getInputField();

            var self = this;
            var duration = 500;

            this.pagerTransition.animate({
                opacity: 0
            }, {
                'duration': duration,
                'complete': function() {
                    inputfield.replaceWith(itemClass.html);
                    self.page = new itemClass();

                    self.pagerTransition.animate({
                        opacity: 1
                    }, {
                        'duration': duration,
                        'complete': function() {
                            self.allowed = true;
                            self.setEnabled(true, false);
                        }
                    });
                }
            });
        };

        this.submit = function() {
            var data = {
                'phone': this.data['phone'],
                'identifier': this.data['identifier']
            };

            var form = this.confirmButton.parent();

            for (var key in data) {
                if (data.hasOwnProperty(key)) {
                    value = data[key];
                    form.append(
                        '<input type="hidden" name="login-' + key + '" value="' + value + '"/>'
                    );
                }
            }

            form.submit();
        };

        this.init();
    };

    var PhoneField = function() {
        this.confirmButton = $("#login-confirm");

        this.init = function() {
            this.element = $(PhoneField.selector);

            var self = this;

            this.element.intlTelInput({
                onlyCountries: [
                    'be',
                    'nl',
                    'fr',
                    'lu',
                    'de'
                ],
                utilsScript: '/static/utils.js'
            }).done(function() {
                self.onChange();
            });
        };

        this.isValid = function() {
            return this.element.intlTelInput('isValidNumber');
        };

        this.getNumber = function() {
            return this.element.intlTelInput('getNumber');
        };

        this.onChange = function() {
            pager.setEnabled(
                true,
                this.isValid()
            );
        };

        this.onConfirm = function()  {
            if (!this.isValid()) {
                alert('Gelieve niets speciaal te proberen, bedankt!');
                return false;
            }

            this.register();
        };

        this.register = function() {
            pager.setEnabled(false, false);
            pager.allowed = false;

            var phone = this.getNumber();
            var self = this;

            PhoneField.requestPin(
                phone,
                function(data, status, request) {
                    var statusCode;
                    if (request === undefined)
                        statusCode = 201;
                    else
                        statusCode = request.statusCode().status;

                    pager.data['phone'] = phone;

                    if (statusCode === 201) {
                        // New user, ask for the name
                        pager.switchPage(NameField.position);
                    } else {
                        // Existing user, skip to the pin code
                        pager.switchPage(PinField.position);
                    }
                },
                function(request, status, error) {
                    pager.subscript.text(messages['error-general']);
                    pager.allowed = true;
                    pager.setEnabled(true, true);
                },
                function() {
                    pager.subscript.text(messages['timeout']);
                }
            )
        };

        this.init();
    };

    PhoneField.requestPin = function(phone, success, error, timeout) {
        pager.subscript.text(messages['pin-request']);

        $.ajax({
            'type': 'POST',
            'data': JSON.stringify({
                'phone': phone
            }),
            'url': '/api/customers/user/register/',
            'contentType': 'application/json; charset=utf-8',
            'success': success,
            'error': error,
            'timeout': timeout
        });
    };

    var NameField = function() {

        this.init = function() {
            this.element = $(NameField.selector);
            pager.subscript.text(messages['namefield-subscript']);
        };

        this.isValid = function() {
            return this.element.val().trim().split(' ').length > 1;
        };

        this.onChange = function() {
            pager.setEnabled(
                true,
                this.isValid()
            );
        };

        this.onConfirm = function() {
            if (!this.isValid())
                return false;

            pager.data['name'] = this.element.val().trim();
            pager.switchPage(PinField.position);
        };

        this.init();
    };

    var PinField = function() {
        this.resendClass = 'resend-pin';
        this.resendHtml = '<br /><a class="' + this.resendClass + '">Code opnieuw verzenden</a>';
        this.timeoutDelay = 30000;
        this.timeoutId;

        this.init = function() {
            this.element = $(PinField.selector);
            this.editSubscript('Kijk mama, zonder wachtwoord!');

            var self = this;
            pager.subscript.on('click', '.' + this.resendClass, function(event) {
                PhoneField.requestPin(
                    pager.data['phone'],
                    function(data, status, request) {
                        self.editSubscript(messages['pin-sent'])
                    },
                    function(request, status, error) {
                        self.editSubscript(messages['error-general']);
                    },
                    function() {
                        self.editSubscript(messages['timeout']);
                    }
                );
                event.preventDefault();
                return false;
            });
        };

        this.login = function() {
            var data = {
                'phone': pager.data['phone'],
                'name': pager.data['name'],
                'pin': pager.data['pin'],
                'token': {
                    'device': Cookies.get('device')
                }
            };

            var self = this;
            $.ajax({
                'type': 'POST',
                'data': JSON.stringify(data),
                'url': '/api/customers/user/login/',
                'contentType': 'application/json; charset=utf-8',
                'dataType': 'json',
                'success': function(data, status, request) {
                    pager.data['identifier'] = data['identifier'];
                    pager.submit();
                },
                'error': function(request, status, error) {
                    self.editSubscript(getErrorMessage(request));
                },
                'timeout': function() {
                    self.editSubscript(messages['timeout']);
                }
            });
        };

        this.isValid = function() {
            var value = this.element.val();
            return value.length == 6 && parseInt(value) !== NaN;
        };

        this.onChange = function() {
            pager.setEnabled(
                true,
                this.isValid()
            );
        };

        this.onConfirm = function() {
            if (!this.isValid())
                return false;
            pager.data['pin'] = this.element.val();
            this.login();
        };

        this.editSubscript = function(text) {
            pager.subscript.text(text);
            window.clearTimeout(this.timeoutId);

            var self = this;
            this.timeoutId = window.setTimeout(
                function() {
                    self.addResendOption();
                },
                this.timeoutDelay
            );
        };

        this.addResendOption = function() {
            pager.subscript.append(this.resendHtml);
        };

        this.init();

    };

    $(document).ready(function() {
        pager = new Pager([{
            'class': PhoneField,
            'selector': '#login-phone'
        }, {
            'class': NameField,
            'selector': '#login-name'
        }, {
            'class': PinField,
            'selector': '#login-pin'
        }]);
    });
})();
