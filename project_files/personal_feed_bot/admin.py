from django.contrib import admin
from .models import BotUser, ConnectedChannels, TempData, FeedChannel


@admin.action(description='Custom Delete Selected Feed Channels')
def delete_selected_feed_channels(modeladmin, request, queryset):
    for f in queryset:
        f.delete()


class FeedChannelAdmin(admin.ModelAdmin):
    actions = [delete_selected_feed_channels,]


@admin.action(description='Custom Delete Selected Connected Channels')
def delete_selected_connected_channels(modeladmin, request, queryset):
    for f in queryset:
        f.delete()


class ConnectedChannelAdmin(admin.ModelAdmin):
    actions = [delete_selected_connected_channels,]
    list_display = ['owner_user', 'channel_username']


@admin.action(description='Custom Delete Selected Bot Users')
def delete_selected_bot_users(modeladmin, request, queryset):
    for f in queryset:
        f.delete()


class BotUserAdmin(admin.ModelAdmin):
    actions = [delete_selected_bot_users,]


@admin.action(description='Custom Delete Selected Temp Data')
def delete_selected_temp_data(modeladmin, request, queryset):
    for f in queryset:
        f.delete()


class TempDataAdmin(admin.ModelAdmin):
    actions = [delete_selected_temp_data,]


# Register your models here.
admin.site.register(BotUser, BotUserAdmin)
admin.site.register(ConnectedChannels, ConnectedChannelAdmin)
admin.site.register(TempData, TempDataAdmin)
admin.site.register(FeedChannel, FeedChannelAdmin)
