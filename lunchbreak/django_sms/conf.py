from datetime import timedelta


class Settings:

    @property
    def settings(self):
        from django.conf import settings
        return getattr(settings, 'SMS', {})

    @property
    def EXPIRY_TIME(self):
        return self.settings.get(
            'expiry_time',
            timedelta(minutes=15)
        )

    @property
    def TIMEOUT(self):
        return self.settings.get(
            'timeout',
            timedelta(seconds=30)
        )

    @property
    def RETRY_TIMEOUT(self):
        return self.settings.get(
            'retry_timeout',
            timedelta(hours=2)
        )

    @property
    def MAX_TRIES(self):
        return self.settings.get(
            'max_tries',
            3
        )

    @property
    def TEXT_TEMPLATE(self):
        # 'Hi, here is your code: {code}.'
        return self.settings['text_template']

    @property
    def DOMAIN(self):
        return self.settings['domain']

    @property
    def PLIVO_SETTINGS(self):
        return self.settings['plivo']

    @property
    def PLIVO_PHONE(self):
        return self.PLIVO_SETTINGS['phone']

    @property
    def PLIVO_AUTH_ID(self):
        return self.PLIVO_SETTINGS['auth_id']

    @property
    def PLIVO_AUTH_TOKEN(self):
        return self.PLIVO_SETTINGS['auth_token']

    @property
    def PLIVO_WEBHOOK_URL(self):
        return self.PLIVO_SETTINGS['webhook_url']

    @property
    def TWILIO_SETTINGS(self):
        return self.settings['twilio']

    @property
    def TWILIO_PHONE(self):
        return self.TWILIO_SETTINGS['phone']

    @property
    def TWILIO_ACCOUNT_SID(self):
        return self.TWILIO_SETTINGS['account_sid']

    @property
    def TWILIO_AUTH_TOKEN(self):
        return self.TWILIO_SETTINGS['auth_token']

    @property
    def TWILIO_WEBHOOK_URL(self):
        return self.TWILIO_SETTINGS['webhook_url']

settings = Settings()  # NOQA
