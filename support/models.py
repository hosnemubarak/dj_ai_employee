from django.db import models
from orders.models import Order

# Create your models here.
class Conversation(models.Model):
    user = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation with {self.user} regarding Order {self.order.id}"

class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('agent', 'Agent'),
    ]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.role} at {self.created_at}"


class AgentLog(models.Model):
    EVENT_CHOICES = [
        ("support", "Support Agent"),
        ("tool_call", "Tool Call"),
        ("tool_result", "Tool Result"),
        ("manager", "Manager Agent"),
        ("risk", "Risk Agent"),
        ("final", "Final Reply"),
    ]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='agent_logs')
    event_type = models.CharField(max_length=100, choices=EVENT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AgentLog: {self.event_type} at {self.created_at}"
