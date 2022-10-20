from django.contrib import admin
from . import models

# Register your models here.
class registerModelValidate(admin.ModelAdmin):
    model = models.validate
    list_display = (
        "token",
        "code",
        "attempt",
        "validate",
        "email",
        "updated_at",
        "created_at",
    )


admin.site.register(models.validate, registerModelValidate)


class loginA(admin.ModelAdmin):
    model = models.loginAttempts
    list_display = ("ipaddress", "attempt", "updated_at", "created_at")


admin.site.register(models.loginAttempts, loginA)
