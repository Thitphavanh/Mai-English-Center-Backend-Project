from django.contrib import admin
from .models import PopupMessage

@admin.register(PopupMessage)
class PopupMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'message')
    filter_horizontal = ('target_users',)
