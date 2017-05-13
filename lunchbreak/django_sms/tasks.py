import logging

import plivo
from celery import shared_task
from Lunchbreak.tasks import DebugLoggingTask
from twilio.base.exceptions import TwilioException, TwilioRestException
from twilio.rest import Client as TwilioClient

from .conf import settings

logger = logging.getLogger('lunchbreak')


@shared_task(base=DebugLoggingTask)
def send_pin(phone_pk):
    from .models import Phone
    phone = Phone.objects.select_related(
        'last_confirmed_message'
    ).get(
        pk=phone_pk
    )
    phone.reset_pin()
    send_message(
        phone=phone,
        body=settings.TEXT_TEMPLATE.format(
            pin=phone.pin
        )
    )


def send_message(phone, body):
    from .models import Message

    if phone.last_confirmed_message is not None:
        gateway = phone.last_confirmed_message.gateway
    else:
        last_message = phone.last_message
        use_plivo = last_message is None or (
            last_message.gateway == Message.PLIVO and
            last_message.success
        ) or (
            last_message.gateway == Message.TWILIO and
            last_message.failure
        )
        gateway = Message.PLIVO if use_plivo else Message.TWILIO

    if gateway == Message.PLIVO:
        message = send_message_plivo(phone, body)
    else:
        message = send_message_twilio(phone, body)

    if message is None or message.failure:
        if gateway == Message.PLIVO:
            message = send_message_twilio(phone, body)
        else:
            message = send_message_plivo(phone, body)


def send_message_plivo(phone, body):
    api = plivo.RestAPI(
        settings.PLIVO_AUTH_ID,
        settings.PLIVO_AUTH_TOKEN
    )
    plivo_message = api.Message.send(
        src=settings.PLIVO_PHONE,
        dst=str(phone.phone),
        text=body,
        url=settings.PLIVO_WEBHOOK_URL
    )

    from .models import Message
    message = Message(
        phone=phone,
        gateway=Message.PLIVO
    )

    if plivo_message.status_code != 202:
        logger.exception(
            'Failed to send Plivo message.',
            extra={
                'phone': phone,
                'body': body,
                'plivo_message.status_code': plivo_message.status_code,
                'plivo_message.json_data': plivo_message.json_data
            }
        )

        message.status = Message.FAILED
        message.error = (
            'Status code {status_code}, JSON data: \n{json_data}'.format(
                status_code=plivo_message.status_code,
                json_data=plivo_message.json_data
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
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    from .models import Message
    message = Message(
        phone=phone,
        gateway=Message.TWILIO
    )

    try:
        twilio_message = client.messages.create(
            to=str(phone.phone),
            from_=settings.TWILIO_PHONE,
            body=body,
            status_callback=settings.TWILIO_WEBHOOK_URL
        )
    except TwilioRestException as e:
        logger.exception(
            str(e),
            exc_info=True,
            extra={
                'phone': phone,
                'body': body,
                'exception uri': getattr(e, 'uri', '?'),
                'exception status': getattr(e, 'status', '?'),
                'exception msg': getattr(e, 'msg', '?'),
                'exception code': getattr(e, 'code', '?'),
                'exception method': getattr(e, 'method', '?'),
            }
        )

        message.status = Message.FAILED
        message.error = (
            'uri: {uri}\n'
            'status: {status}\n'
            'msg: {msg}\n'
            'code: {code}\n'
            'method: {method}\n'.format(
                uri=getattr(e, 'uri', '?'),
                status=getattr(e, 'status', '?'),
                msg=getattr(e, 'msg', '?'),
                code=getattr(e, 'code', '?'),
                method=getattr(e, 'method', '?')
            )
        )
        message.save()
        return message
    except TwilioException as e:
        logger.exception(
            str(e),
            exc_info=True,
            extra={
                'phone': phone,
                'body': body,
                'exception uri': getattr(e, 'uri', '?'),
                'exception status': getattr(e, 'status', '?'),
                'exception msg': getattr(e, 'msg', '?'),
                'exception code': getattr(e, 'code', '?'),
                'exception method': getattr(e, 'method', '?'),
            }
        )

        message.status = Message.FAILED
        message.error = str(e)
        message.save()
        return message

    message.remote_uuid = twilio_message.sid[2:]
    message.status = twilio_message.status
    message.save()
    return message
