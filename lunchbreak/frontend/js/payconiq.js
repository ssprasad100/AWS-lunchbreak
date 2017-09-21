(function() {
    'use strict';

    var timeout = 5000;

    var redirect = function(url) {
        window.location.href = url;
    };

    $(document).ready(function() {
        var info = $('#payconiq-info')
        payconiq({
            widgetType: 'popup',
            transactionData: {
                webhookId: webhookId,
                signature: signature,
                merchantId: merchantId,
                amount: amount,
                currency: currency,
                returnUrl: successUrl
            }
        }).on('success', function() {
            info.text('Betaling succesvol verlopen, je wordt doorverwezen naar de bevestigingspagina...');

            setTimeout(function() {
                redirect(successUrl);
            }, 0);
        }).on('failed', function() {
            info.text('Betaling gefaald, je wordt terug gestuurd naar naar de vorige pagina...');

            setTimeout(function() {
                redirect(errorUrl);
            }, timeout);
        }).on('canceled', function() {
            info.text('Betaling geannuleerd, je wordt terug gestuurd naar naar de vorige pagina...');

            setTimeout(function() {
                redirect(errorUrl);
            }, timeout);
        }).on('close', function() {
            info.text('Betaling geannuleerd, je wordt terug gestuurd naar naar de vorige pagina...');

            setTimeout(function() {
                redirect(errorUrl);
            }, timeout);
        }).on('error', function() {
            info.text('Er is een fout opgetreden tijdens de betaling, je wordt terug gestuurd naar naar de vorige pagina...');

            setTimeout(function() {
                redirect(errorUrl);
            }, timeout);
        }).load();
    });
})();


