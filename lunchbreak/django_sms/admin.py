from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Message, Phone


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created_at', 'confirmed_at', 'last_message',)
    search_fields = ('phone',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('phone', 'status', 'gateway', 'sent_at',)
    search_fields = ('id', 'remote_uuid', 'phone__phone',)
    list_filter = ('gateway', 'status',)
    ordering = ('-sent_at',)

    readonly_fields = ('id', 'remote_uuid', 'gateway', 'error',)

    fieldsets = (
        (
            _('Basis gegevens'),
            {
                'fields': ('phone', 'gateway', 'status', 'sent_at', 'error')
            },
        ),
        (
            _('Technische gegevens'),
            {
                'fields': ('id', 'remote_uuid',)
            },
        ),
    )
