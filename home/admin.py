from django.contrib import admin
from .models import SchoolHistory, Announcement, NewsActivity, OrgChart

@admin.register(SchoolHistory)
class SchoolHistoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_active')
    list_filter = ('is_active',)

@admin.register(NewsActivity)
class NewsActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')

@admin.register(OrgChart)
class OrgChartAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at')
