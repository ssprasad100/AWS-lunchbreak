import json

import plivo
from celery import shared_task
from Lunchbreak.tasks import DebugLoggingTask
from twilio.base.exceptions import TwilioException, TwilioRestException
from twilio.rest import Client as TwilioClient

from .conf import (PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN, PLIVO_PHONE,
                   PLIVO_WEBHOOK_URL, TEXT_TEMPLATE, TWILIO_ACCOUNT_SID,
                   TWILIO_AUTH_TOKEN, TWILIO_PHONE, TWILIO_WEBHOOK_URL)


@shared_task(base=DebugLoggingTask)
def send_pin(phone_pk):
    from .models import Phone
    phone = Phone.objects.get(
        pk=phone_pk
    )
    phone.reset_pin()
    send_message(
        phone=phone,
        body=TEXT_TEMPLATE.format(
            pin=phone.pin
        )
    )


def send_message(phone, body):
    from .models import Message

    last_message = phone.last_message
    use_plivo = last_message is None or (
        last_message.gateway == Message.PLIVO and
        last_message.success
    ) or (
        last_message.gateway == Message.TWILIO and
        last_message.failure
    )

    if use_plivo:
        message = send_message_plivo(phone, body)
    else:
        message = send_message_twilio(phone, body)

    if message is None or message.failure:
        if use_plivo:
            message = send_message_twilio(phone, body)
        else:
            message = send_message_plivo(phone, body)


def send_message_plivo(phone, body):
    api = plivo.RestAPI(
        PLIVO_AUTH_ID,
        PLIVO_AUTH_TOKEN
    )
    plivo_message = api.Message.send(
        src=PLIVO_PHONE,
        dst=str(phone.phone),
        text=body,
        url=PLIVO_WEBHOOK_URL
    )

    from .models import Message
    message = Message(
        phone=phone,
        gateway=Message.PLIVO
    )

    if plivo_message.status_code != 202:
        message.status = Message.FAILED
        message.error = (
            'Status code {status_code}, JSON data: \n{json_data}'.format(
                status_code=plivo_message.status_code,
                json_data=json.dumps(
                    plivo_message.json_data,
                    indent=4
                )
            )
        )
        message.save()
        return message

    # Split messages are not supported.
    message.remote_uuid = plivo_message.json_data['message_uuid'][0]
    message.save()
    return message


def send_message_twilio(phone, body):
    client = TwilioClient(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN
    )

    from .models import Message
    message = Message(
        phone=phone,
        gateway=Message.TWILIO
    )

    try:
        twilio_message = client.messages.create(
            to=str(phone.phone),
            from_=TWILIO_PHONE,
            body=body,
            status_callback=TWILIO_WEBHOOK_URL
        )
    except TwilioRestException as e:
        message.status = Message.FAILED
        message.error = (
            'uri: {uri}\n'
            'status: {status}\n'
            'msg: {msg}\n'
            'code: {code}\n'
            'method: {method}\n'.format(
                uri=e.uri,
                status=e.status,
                msg=e.msg,
                code=e.code,
                method=e.method
            )
        )
        message.save()
        return message
    except TwilioException as e:
        message.status = Message.FAILED
        message.error = str(e)
        message.save()
        return message

    message.remote_uuid = twilio_message.sid[2:]
    message.status = twilio_message.status
    message.save()
    return message
