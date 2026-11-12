from django.contrib import admin

from .models import AgentLog, Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user", "order__product_name", "order__tracking_number")
    date_hierarchy = "created_at"
    list_select_related = ("order",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content", "conversation__user", "conversation__order__product_name")
    date_hierarchy = "created_at"
    list_select_related = ("conversation", "conversation__order")


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "event_type", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = (
        "message",
        "conversation__user",
        "conversation__order__product_name",
    )
    date_hierarchy = "created_at"
    list_select_related = ("conversation", "conversation__order")
