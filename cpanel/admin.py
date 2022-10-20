from django.contrib import admin
from . import models


class prediction(admin.ModelAdmin):
    model = models.pancakeswapPredicition
    list_display = ("epoch", "bull", "bear", "wallet_number", "claimable", "bet_type")


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
