from django.contrib import admin
from .models import EmailVerification


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'is_confirmed', 'created_at')
    list_filter = ('is_confirmed',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
