from django.contrib import admin

from .models import Announcement, AnnouncementAttachment, AnnouncementView


class AnnouncementAttachmentInline(admin.TabularInline):
    model = AnnouncementAttachment
    extra = 1


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'priority', 'audience', 'pinned', 'published', 'created_at']
    list_filter = ['priority', 'audience', 'pinned', 'published', 'created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    inlines = [AnnouncementAttachmentInline]
    filter_horizontal = ['target_classrooms']


@admin.register(AnnouncementView)
class AnnouncementViewAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['announcement__title', 'user__username']
