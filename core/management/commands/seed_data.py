from django.core.management.base import BaseCommand
from core.models import KnowledgeArticle, Ticket, ChatMessage, LogAnalysis

class Command(BaseCommand):
    help = 'Seeds knowledge base and resets operational data to zero for real-world use'
    
    def handle(self, *args, **options):
        # Clear out any demo tickets, chats, and log analyses so everything starts fresh at zero
        Ticket.objects.all().delete()
        ChatMessage.objects.all().delete()
        LogAnalysis.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Reset all tickets, chats, and log analyses to ZERO (0).'))
        
        # Ensure knowledge base articles exist for real troubleshooting
        if not KnowledgeArticle.objects.exists():
            articles = [
                {'title': 'WiFi & Internet Connectivity Troubleshooting Guide', 'category': 'Network', 'content': 'Complete guide to resolving WiFi and internet connectivity issues including driver updates, network reset commands, and DHCP lease renewal.', 'tags': ['wifi', 'internet', 'network', 'connectivity']},
                {'title': 'VPN Connection Issues & Solutions', 'category': 'Network', 'content': 'Step-by-step guide for troubleshooting VPN connections, protocol switching (UDP/TCP), firewall rules, and certificate validation.', 'tags': ['vpn', 'remote', 'network']},
                {'title': 'Password Reset & Account Recovery Guide', 'category': 'Access', 'content': 'How to reset your password via self-service portal, verify identity using MFA, and resolve Active Directory account lockouts.', 'tags': ['password', 'login', 'access', 'account']},
                {'title': 'Email & Outlook Troubleshooting', 'category': 'Software', 'content': 'Fixing common email sending/receiving errors, clearing Outlook RoamCache, repairing PST/OST profiles, and attachment limits.', 'tags': ['email', 'outlook', 'mail']},
                {'title': 'Printer Setup & Troubleshooting', 'category': 'Hardware', 'content': 'Resolving printer offline status, clearing Windows Print Spooler queue, driver re-installation, and IP port mapping.', 'tags': ['printer', 'printing', 'hardware']},
                {'title': 'Blue Screen of Death (BSOD) Fix Guide', 'category': 'Hardware', 'content': 'Understanding STOP codes, booting into Safe Mode, running System File Checker (sfc /scannow), and memory diagnostic tests.', 'tags': ['bsod', 'crash', 'blue screen']},
                {'title': 'Improving Computer Performance', 'category': 'Software', 'content': 'Speed up slow workstations by analyzing Task Manager resource bottlenecks, disabling startup items, and running Disk Cleanup.', 'tags': ['slow', 'performance', 'speed']},
                {'title': 'Software Installation Troubleshooting', 'category': 'Software', 'content': 'Resolving installer permission errors (Error 1603), missing C++ redistributables, administrator elevation, and registry cleanup.', 'tags': ['install', 'software', 'setup']},
                {'title': 'Security Threat Response Playbook', 'category': 'Security', 'content': 'Standard Operating Procedure when phishing emails, malware alerts, or unauthorized logins occur. Network isolation and password resets.', 'tags': ['security', 'virus', 'malware', 'phishing']},
                {'title': 'Managing Disk Space & Storage', 'category': 'Hardware', 'content': 'Freeing up drive space on Windows C: drive, clearing temp folders, analyzing WinDirStat storage distribution, and cloud migration.', 'tags': ['disk', 'storage', 'space']},
                {'title': 'Microsoft Teams Troubleshooting', 'category': 'Software', 'content': 'Resolving Teams audio/video device selection errors, clearing Teams cache (%appdata%\\Microsoft\\Teams), and web client fallbacks.', 'tags': ['teams', 'video', 'audio', 'collaboration']},
                {'title': 'Network Drive Mapping Guide', 'category': 'Network', 'content': 'How to map SMB network shares via net use, resolve credentials prompt loops, and troubleshoot SMB port 445 blockages.', 'tags': ['network drive', 'mapping', 'shared folder']},
            ]
            for a in articles:
                KnowledgeArticle.objects.create(**a)
            self.stdout.write(self.style.SUCCESS(f'Seeded {len(articles)} knowledge base articles for AI engine.'))
        else:
            self.stdout.write('Knowledge base articles already present.')
