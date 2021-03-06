from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from Lunchbreak.tasks import DebugLoggingTask


@shared_task(base=DebugLoggingTask)
def send_group_order_email(group_order_id):
    from .models import GroupOrder
    try:
        group_order = GroupOrder.objects.select_related(
            'group__store'
        ).get(
            pk=group_order_id
        )
    except GroupOrder.DoesNotExist:
        return

    if group_order.orders.count() == 0:
        return

    send_email(
        subject=_('Groepsbestelling %(store)s') % {
            'store': group_order.group.store.name
        },
        recipients=[group_order.group.email],
        template='group_order',
        template_args={
            'group_order': group_order
        }
    )


@shared_task(base=DebugLoggingTask)
def send_group_created_emails(group_id):
    from .models import Group
    try:
        group = Group.objects.select_related(
            'store'
        ).get(
            pk=group_id
        )
    except Group.DoesNotExist as e:
        return

    send_email(
        subject=_('Welkom bij Lunchbreak!'),
        recipients=[group.email],
        template='group_join',
        template_args={
            'group': group
        }
    )
    send_email(
        subject=_('Lunchbreak groep aangemaakt!'),
        recipients=[group.email],
        template='group_created',
        template_args={
            'group': group
        }
    )


@shared_task(base=DebugLoggingTask)
def send_email(subject, recipients, template, template_args={}):
    message = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string(
            template + '.txt',
            template_args
        ),
        from_email=settings.EMAIL_FROM,
        to=recipients
    )
    message.attach_alternative(
        render_to_string(
            template + '.html',
            template_args
        ),
        'text/html'
    )
    message.send()
