import pendulum
import plivo
from celery import shared_task
from Lunchbreak.tasks import DebugLoggingTask
from twilio import TwilioRestException
from twilio.rest import Client as TwilioClient

from .conf import (GATEWAY_PLIVO, GATEWAY_TWILIO, PLIVO_AUTH_ID,
                   PLIVO_AUTH_TOKEN, PLIVO_PHONE, TEXT_TEMPLATE,
                   TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE)


@shared_task(base=DebugLoggingTask)
def send_pin(phone_pk):
    from .models import Phone
    try:
        phone = Phone.objects.get(
            pk=phone_pk
        )
    except Phone.DoesNotExist:
        return
    phone.new_pin()
    send_message(
        phone=phone,
        body=TEXT_TEMPLATE.format(
            pin=phone.pin
        )
    )


def send_message(phone, body):
    last_message = phone.last_message
    use_plivo = last_message is None or (
        last_message.gateway == GATEWAY_PLIVO and
        last_message.success
    ) or (
        last_message.gateway == GATEWAY_TWILIO and
        last_message.failure
    )

    if use_plivo:
        message = send_message_plivo(str(phone.phone), body)
    else:
        message = send_message_twilio(str(phone.phone), body)

    if message is None or message.failed:
        if use_plivo:
            message = send_message_twilio(str(phone.phone), body)
        else:
            message = send_message_plivo(str(phone.phone), body)


def send_message_plivo(phone, body):
    api = plivo.RestAPI(
        PLIVO_AUTH_ID,
        PLIVO_AUTH_TOKEN
    )
    message = api.Message.send(
        src=PLIVO_PHONE,
        dst=phone,
        text=body,
        url=''
    )

    if message.status_code != 202:
        return None

    # Split messages are not supported.
    uuid = message.json_data['message_uid'][0]

    from .models import Message
    return Message.objects.create(
        id=uuid,
        phone=phone,
        gateway=GATEWAY_PLIVO
    )


def send_message_twilio(phone, body):
    client = TwilioClient(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN
    )
    try:
        message = client.messages.create(
            to=phone,
            from_=TWILIO_PHONE,
            body=body,
            status_callback=''
        )
    except TwilioRestException:
        return None

    from .models import Message
    return Message.objects.create(
        id=message['sid'][2:],
        phone=phone,
        gateway=GATEWAY_TWILIO,
        status=message['status'],
        sent_at=pendulum.parse(message['date_sent'])._datetime,
    )
