from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from django.apps import apps


@shared_task()
def send_group_order_email(group_order_id):
    GroupOrder = apps.get_model('GroupOrder')

    try:
        group_order = GroupOrder.objects.select_related(
            'group__store'
        ).get(
            pk=group_order_id
        )
    except GroupOrder.DoesNotExist:
        return

    if len(group_order.orders) == 0:
        return

    return send_email(
        subject=_('Groepsbestelling %(store)s') % {
            'store': group_order.group.store.name
        },
        recipients=[group_order.group.email],
        plaintext_template='group_order.txt',
        html_template='group_order.html',
        template_args={
            'group_order': group_order
        }
    )


@shared_task
def send_email(subject, recipients, plaintext_template, sender=None,
               html_template=None, template_args={}):
    if sender is None:
        sender = settings.EMAIL_FROM

    text_content = render_to_string(
        plaintext_template,
        template_args
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=sender,
        to=recipients
    )

    if html_template is not None:
        message.attach_alternative(
            render_to_string(
                html_template,
                template_args
            ),
            'text/html'
        )

    return message.send()
