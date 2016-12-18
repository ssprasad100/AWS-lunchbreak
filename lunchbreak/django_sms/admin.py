from django.contrib import admin

from .models import Phone


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created_at', 'confirmed_at', 'last_message',)
    search_fields = ('phone',)
