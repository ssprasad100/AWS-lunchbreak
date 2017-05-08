from django.contrib import admin

from .models import Merchant, Transaction


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'remote_id',)
    search_fields = ('name', 'id', 'remote_id',)
    ordering = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'remote_id', 'amount', 'currency', 'status',)
    search_fields = ('id', 'remote_id',)
    list_filter = ('status',)
    ordering = ('id',)
