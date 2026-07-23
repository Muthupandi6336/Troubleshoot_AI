from django.db import models
from django.db.models import CharField, TextField, JSONField, DateTimeField, FloatField, IntegerField

class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('network', 'Network'),
        ('security', 'Security'),
        ('access', 'Access & Permissions'),
        ('other', 'Other'),
    ]
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    title = CharField(max_length=255)
    description = TextField()
    category = CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    priority = CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    sentiment = CharField(max_length=20, default='neutral')  # positive, neutral, negative, frustrated
    ai_suggestion = TextField(blank=True, null=True)
    created_by = CharField(max_length=100, default='User')
    assigned_to = CharField(max_length=100, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    resolved_at = DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.status}"

class ChatMessage(models.Model):
    session_id = CharField(max_length=100)
    role = CharField(max_length=20)  # 'user' or 'assistant'
    content = TextField()
    confidence = FloatField(default=0.0)
    sources = JSONField(default=list, blank=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role} - {self.created_at}"

class KnowledgeArticle(models.Model):
    title = CharField(max_length=255)
    category = CharField(max_length=50)
    content = TextField()
    tags = JSONField(default=list, blank=True)
    views = IntegerField(default=0)
    helpful_count = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class LogAnalysis(models.Model):
    title = CharField(max_length=255)
    raw_log = TextField()
    analysis_result = JSONField(default=dict)
    errors_found = IntegerField(default=0)
    warnings_found = IntegerField(default=0)
    anomalies = JSONField(default=list)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class TicketActivity(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='activities')
    action = CharField(max_length=100)  # e.g., 'created', 'status_changed', 'assigned'
    old_value = CharField(max_length=100, blank=True, null=True)
    new_value = CharField(max_length=100, blank=True, null=True)
    performed_by = CharField(max_length=100, default='System')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket.title} - {self.action}"
