import logging
import traceback

from celery import Task, shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

logger = logging.getLogger('lunchbreak')


class ErrorLoggingTask(Task):
    """Base Celery task for logging errors."""
    abstract = True

    def on_failure(self, exception, *args, **kwargs):
        """Log the exceptions to sentry."""

        if settings.DEBUG:
            traceback.print_exc()
        else:
            logger.exception(
                str(exception),
                exc_info=True,
                extra=dict(kwargs, **{
                    'arguments': args
                })
            )
        super().on_failure(exception, *args, **kwargs)


@shared_task(base=ErrorLoggingTask)
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

    if len(group_order.orders) == 0:
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


@shared_task(base=ErrorLoggingTask)
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


@shared_task(base=ErrorLoggingTask)
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
