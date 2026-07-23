from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('tickets/', views.tickets_view, name='tickets'),
    path('log-analyzer/', views.log_analyzer_view, name='log_analyzer'),
    path('knowledge-base/', views.knowledge_base_view, name='knowledge_base'),
    
    # API endpoints
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/chat/clear/', views.api_chat_clear, name='api_chat_clear'),
    path('api/tickets/', views.api_tickets, name='api_tickets'),
    path('api/tickets/<int:ticket_id>/update/', views.api_ticket_update, name='api_ticket_update'),
    path('api/tickets/<int:ticket_id>/activities/', views.api_ticket_activities, name='api_ticket_activities'),
    path('api/logs/analyze/', views.api_analyze_logs, name='api_analyze_logs'),
    path('api/knowledge/', views.api_knowledge, name='api_knowledge'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/tickets/export/csv/', views.export_tickets_csv, name='export_tickets_csv'),
]
