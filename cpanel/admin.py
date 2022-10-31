from django.contrib import admin
from . import models


class prediction(admin.ModelAdmin):
    model = models.pancakeswapPredicition
    list_display = (
        "epoch",
        "bull",
        "bear",
        "wallet_number",
        "claimable",
        "claimed",
        "bet_type",
        "transaction_hash",
        "created_at",
    )


admin.site.register(models.pancakeswapPredicition, prediction)


class server_status(admin.ModelAdmin):
    model = models.server_status
    list_display = (
        "status",
        "logging",
        "started_at",
        "stoped_at",
        "updated_at",
        "created_at",
    )


admin.site.register(models.server_status, server_status)


class logging(admin.ModelAdmin):
    model = models.message_logging
    list_display = ("created_at", "message")


admin.site.register(models.message_logging, logging)


class transaction_hash(admin.ModelAdmin):
    model = models.transaction_hash
    list_display = ("epoch", "transaction_hash", "wallet_number", "created_at")


admin.site.register(models.transaction_hash, transaction_hash)


class threading(admin.ModelAdmin):
    model = models.thread_value
    list_display = ("x",)


admin.site.register(models.thread_value, threading)
