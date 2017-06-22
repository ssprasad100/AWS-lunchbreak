(function() {
    'use strict';

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
            window.location.href = successUrl;
        }).on('failed', function() {
            info.text('Betaling gefaald, je wordt terug gestuurd naar naar de vorige pagina...');
            window.location.href = errorUrl;
        }).on('canceled', function() {
            info.text('Betaling geannuleerd, je wordt terug gestuurd naar naar de vorige pagina...');
            window.location.href = errorUrl;
        }).on('close', function() {
            info.text('Betaling geannuleerd, je wordt terug gestuurd naar naar de vorige pagina...');
            window.location.href = errorUrl;
        }).on('error', function() {
            info.text('Er is een fout opgetreden tijdens de betaling, je wordt terug gestuurd naar naar de vorige pagina...');
            window.location.href = errorUrl;
        }).load();
    });
})();


