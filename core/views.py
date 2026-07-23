import json
import uuid
import csv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from .models import Ticket, ChatMessage, KnowledgeArticle, LogAnalysis, TicketActivity
from .ai_engine import ai_engine

# Page Views
def index(request):
    return render(request, 'core/index.html')

def dashboard(request):
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    in_progress = Ticket.objects.filter(status='in_progress').count()
    
    # Category distribution
    categories = {}
    for choice in Ticket.CATEGORY_CHOICES:
        categories[choice[1]] = Ticket.objects.filter(category=choice[0]).count()
    
    # Priority distribution
    priorities = {}
    for choice in Ticket.PRIORITY_CHOICES:
        priorities[choice[1]] = Ticket.objects.filter(priority=choice[0]).count()
    
    # Recent tickets
    recent_tickets = Ticket.objects.order_by('-created_at')[:5]
    
    # KB stats
    total_articles = KnowledgeArticle.objects.count()
    total_chats = ChatMessage.objects.filter(role='user').count()
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'resolved_tickets': resolved_tickets,
        'in_progress': in_progress,
        'categories': json.dumps(categories),
        'priorities': json.dumps(priorities),
        'recent_tickets': recent_tickets,
        'total_articles': total_articles,
        'total_chats': total_chats,
        'resolution_rate': round((resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0, 1),
    }
    return render(request, 'core/dashboard.html', context)

def chatbot(request):
    session_id = request.session.get('chat_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['chat_session_id'] = session_id
    
    messages = ChatMessage.objects.filter(session_id=session_id).order_by('created_at')
    return render(request, 'core/chatbot.html', {'messages': messages, 'session_id': session_id})

def tickets_view(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'core/tickets.html', {'tickets': tickets})

def log_analyzer_view(request):
    analyses = LogAnalysis.objects.all().order_by('-created_at')[:10]
    return render(request, 'core/log_analyzer.html', {'analyses': analyses})

def knowledge_base_view(request):
    articles = KnowledgeArticle.objects.all().order_by('-created_at')
    categories = KnowledgeArticle.objects.values_list('category', flat=True).distinct()
    return render(request, 'core/knowledge_base.html', {'articles': articles, 'categories': categories})

# API Endpoints
@csrf_exempt
@require_http_methods(['POST'])
def api_chat(request):
    data = json.loads(request.body)
    message = data.get('message', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # Save user message
    ChatMessage.objects.create(
        session_id=session_id,
        role='user',
        content=message,
    )
    
    # Get AI response
    response = ai_engine.get_response(message)
    
    # Save assistant message
    ChatMessage.objects.create(
        session_id=session_id,
        role='assistant',
        content=response['message'],
        confidence=response['confidence'],
        sources=response['sources'],
    )
    
    return JsonResponse({
        'message': response['message'],
        'confidence': response['confidence'],
        'sources': response['sources'],
        'category': response['category'],
    })

@csrf_exempt
@require_http_methods(['POST', 'GET'])
def api_tickets(request):
    if request.method == 'GET':
        tickets = Ticket.objects.all().order_by('-created_at')
        data = [{
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'category': t.category,
            'priority': t.priority,
            'status': t.status,
            'sentiment': t.sentiment,
            'ai_suggestion': t.ai_suggestion,
            'created_by': t.created_by,
            'assigned_to': t.assigned_to,
            'created_at': t.created_at.isoformat(),
        } for t in tickets]
        return JsonResponse({'tickets': data})
    
    # POST - Create ticket
    data = json.loads(request.body)
    title = data.get('title', '')
    description = data.get('description', '')
    
    # AI classification
    classification = ai_engine.classify_ticket(title, description)
    
    ticket = Ticket.objects.create(
        title=title,
        description=description,
        category=classification['category'],
        priority=classification['priority'],
        sentiment=classification['sentiment'],
        ai_suggestion=classification['ai_suggestion'],
        created_by=data.get('created_by', 'User'),
    )
    
    TicketActivity.objects.create(
        ticket=ticket,
        action='created',
        new_value=f'{ticket.category} / {ticket.priority}',
        performed_by=data.get('created_by', 'User'),
    )
    
    return JsonResponse({
        'id': ticket.id,
        'title': ticket.title,
        'category': ticket.category,
        'priority': ticket.priority,
        'sentiment': ticket.sentiment,
        'ai_suggestion': ticket.ai_suggestion,
        'status': ticket.status,
        'confidence': classification['confidence'],
        'created_at': ticket.created_at.isoformat(),
    })

@csrf_exempt
@require_http_methods(['POST'])
def api_ticket_update(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)
    
    data = json.loads(request.body)
    if 'status' in data:
        old_status = ticket.status
        ticket.status = data['status']
        if data['status'] == 'resolved':
            ticket.resolved_at = timezone.now()
        TicketActivity.objects.create(
            ticket=ticket,
            action='status_changed',
            old_value=old_status,
            new_value=data['status'],
            performed_by='Agent',
        )
    if 'priority' in data:
        old_priority = ticket.priority
        ticket.priority = data['priority']
        TicketActivity.objects.create(
            ticket=ticket,
            action='priority_changed',
            old_value=old_priority,
            new_value=data['priority'],
            performed_by='Agent',
        )
    if 'assigned_to' in data:
        ticket.assigned_to = data['assigned_to']
        TicketActivity.objects.create(
            ticket=ticket,
            action='assigned',
            new_value=data['assigned_to'],
            performed_by='Agent',
        )
    ticket.save()
    
    return JsonResponse({'success': True, 'id': ticket.id, 'status': ticket.status})

@csrf_exempt
@require_http_methods(['POST'])
def api_analyze_logs(request):
    data = json.loads(request.body)
    log_content = data.get('log_content', '')
    title = data.get('title', f'Log Analysis {timezone.now().strftime("%Y-%m-%d %H:%M")}')
    
    # Analyze logs
    result = ai_engine.analyze_logs(log_content)
    
    # Save analysis
    analysis = LogAnalysis.objects.create(
        title=title,
        raw_log=log_content,
        analysis_result=result,
        errors_found=result['summary']['errors'],
        warnings_found=result['summary']['warnings'],
        anomalies=result['anomalies'],
    )
    
    return JsonResponse({
        'id': analysis.id,
        'title': analysis.title,
        'summary': result['summary'],
        'errors': result['errors'],
        'warnings': result['warnings'],
        'anomalies': result['anomalies'],
        'all_lines': result['all_lines'],
    })

@csrf_exempt
@require_http_methods(['POST', 'GET'])
def api_knowledge(request):
    if request.method == 'GET':
        articles = KnowledgeArticle.objects.all().order_by('-created_at')
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        
        if search:
            articles = articles.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        if category:
            articles = articles.filter(category=category)
        
        data = [{
            'id': a.id,
            'title': a.title,
            'category': a.category,
            'content': a.content,
            'tags': a.tags,
            'views': a.views,
            'helpful_count': a.helpful_count,
            'created_at': a.created_at.isoformat(),
        } for a in articles]
        return JsonResponse({'articles': data})
    
    # POST - Create article
    data = json.loads(request.body)
    article = KnowledgeArticle.objects.create(
        title=data.get('title', ''),
        category=data.get('category', 'general'),
        content=data.get('content', ''),
        tags=data.get('tags', []),
    )
    
    return JsonResponse({
        'id': article.id,
        'title': article.title,
        'category': article.category,
        'created_at': article.created_at.isoformat(),
    })

def api_stats(request):
    """Dashboard statistics API."""
    total = Ticket.objects.count()
    open_t = Ticket.objects.filter(status='open').count()
    resolved = Ticket.objects.filter(status='resolved').count()
    in_progress = Ticket.objects.filter(status='in_progress').count()
    
    categories = {}
    for choice in Ticket.CATEGORY_CHOICES:
        count = Ticket.objects.filter(category=choice[0]).count()
        if count > 0:
            categories[choice[1]] = count
    
    priorities = {}
    for choice in Ticket.PRIORITY_CHOICES:
        count = Ticket.objects.filter(priority=choice[0]).count()
        if count > 0:
            priorities[choice[1]] = count
    
    return JsonResponse({
        'total_tickets': total,
        'open_tickets': open_t,
        'resolved_tickets': resolved,
        'in_progress': in_progress,
        'resolution_rate': round((resolved / total * 100) if total > 0 else 0, 1),
        'categories': categories,
        'priorities': priorities,
        'total_articles': KnowledgeArticle.objects.count(),
        'total_chats': ChatMessage.objects.filter(role='user').count(),
    })

@csrf_exempt
@require_http_methods(['POST', 'GET'])
def api_chat_clear(request):
    session_id = None
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
        except json.JSONDecodeError:
            session_id = request.POST.get('session_id')
    elif request.method == 'GET':
        session_id = request.GET.get('session_id')
        
    if session_id:
        try:
            ChatMessage.objects.filter(session_id=session_id).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    return JsonResponse({'success': False, 'error': 'No session_id provided'}, status=400)

def api_ticket_activities(request, ticket_id):
    """Get activity timeline for a specific ticket."""
    activities = TicketActivity.objects.filter(ticket_id=ticket_id).order_by('-created_at')[:20]
    data = [{
        'action': a.action,
        'old_value': a.old_value,
        'new_value': a.new_value,
        'performed_by': a.performed_by,
        'created_at': a.created_at.isoformat(),
    } for a in activities]
    return JsonResponse({'activities': data})

def export_tickets_csv(request):
    """Export all tickets as a CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="troubleshoot_ai_tickets.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Description', 'Category', 'Priority', 'Status', 'Sentiment', 'AI Suggestion', 'Created By', 'Assigned To', 'Created At', 'Resolved At'])
    tickets = Ticket.objects.all().order_by('-created_at')
    for t in tickets:
        writer.writerow([t.id, t.title, t.description, t.category, t.priority, t.status, t.sentiment, t.ai_suggestion or '', t.created_by, t.assigned_to or '', t.created_at.strftime('%Y-%m-%d %H:%M'), t.resolved_at.strftime('%Y-%m-%d %H:%M') if t.resolved_at else ''])
    return response
