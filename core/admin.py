from django.contrib import admin
from .models import Ticket, ChatMessage, KnowledgeArticle, LogAnalysis

admin.site.register(Ticket)
admin.site.register(ChatMessage)
admin.site.register(KnowledgeArticle)
admin.site.register(LogAnalysis)
