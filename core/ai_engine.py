import re
import json
import random
from difflib import SequenceMatcher

class TroubleshootAI:
    """RAG-ready AI troubleshooting engine with built-in knowledge base."""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Comprehensive IT troubleshooting knowledge base."""
        return {
            'wifi_connectivity': {
                'keywords': ['wifi', 'wi-fi', 'wireless', 'internet', 'connection', 'network', 'cannot connect', 'no internet', 'slow internet', 'disconnecting'],
                'title': 'WiFi & Internet Connectivity Issues',
                'category': 'network',
                'solutions': [
                    {'step': 1, 'action': 'Check if WiFi is enabled on your device', 'detail': 'Look for the WiFi icon in your system tray (Windows) or menu bar (Mac). Ensure it is turned on.'},
                    {'step': 2, 'action': 'Restart your router/modem', 'detail': 'Unplug the power cable, wait 30 seconds, then plug it back in. Wait 2-3 minutes for full restart.'},
                    {'step': 3, 'action': 'Forget and reconnect to the network', 'detail': 'Go to WiFi settings, click on your network, select "Forget", then reconnect with the password.'},
                    {'step': 4, 'action': 'Run network diagnostics', 'detail': 'Windows: Right-click WiFi icon > Troubleshoot. Mac: Option+click WiFi icon > Open Wireless Diagnostics.'},
                    {'step': 5, 'action': 'Reset network settings', 'detail': 'Windows: netsh winsock reset && netsh int ip reset. Mac: System Preferences > Network > Advanced > Renew DHCP Lease.'},
                    {'step': 6, 'action': 'Check for driver updates', 'detail': 'Windows: Device Manager > Network Adapters > Update driver. Mac: System Update.'},
                ]
            },
            'vpn_issues': {
                'keywords': ['vpn', 'virtual private network', 'vpn not connecting', 'vpn slow', 'vpn disconnects', 'tunnel', 'remote access'],
                'title': 'VPN Connection Troubleshooting',
                'category': 'network',
                'solutions': [
                    {'step': 1, 'action': 'Verify your internet connection is working', 'detail': 'Open a browser and try visiting google.com. VPN requires active internet.'},
                    {'step': 2, 'action': 'Check VPN credentials', 'detail': 'Ensure your username, password, and server address are correct. Check if your password has expired.'},
                    {'step': 3, 'action': 'Try a different VPN server/protocol', 'detail': 'Switch between TCP and UDP protocols, or try connecting to a different VPN server.'},
                    {'step': 4, 'action': 'Disable firewall temporarily', 'detail': 'Some firewalls block VPN traffic. Temporarily disable to test, then add VPN as an exception.'},
                    {'step': 5, 'action': 'Clear VPN cache and reconnect', 'detail': 'Close VPN client completely, clear temp files, and restart the application.'},
                ]
            },
            'password_reset': {
                'keywords': ['password', 'reset password', 'forgot password', 'locked out', 'account locked', 'cannot login', 'login failed', 'authentication'],
                'title': 'Password Reset & Account Recovery',
                'category': 'access',
                'solutions': [
                    {'step': 1, 'action': 'Use the self-service password reset portal', 'detail': 'Navigate to https://passwordreset.company.com and follow the prompts.'},
                    {'step': 2, 'action': 'Verify your identity', 'detail': 'Answer security questions or use your registered phone/email for verification.'},
                    {'step': 3, 'action': 'Create a strong new password', 'detail': 'Use at least 12 characters with uppercase, lowercase, numbers, and special characters.'},
                    {'step': 4, 'action': 'Update saved passwords', 'detail': 'Update the password in any saved browsers, email clients, and mobile devices.'},
                    {'step': 5, 'action': 'If still locked, contact IT admin', 'detail': 'Your account may need to be manually unlocked by an administrator.'},
                ]
            },
            'email_issues': {
                'keywords': ['email', 'outlook', 'mail', 'cannot send', 'cannot receive', 'email not working', 'inbox', 'smtp', 'imap'],
                'title': 'Email & Outlook Troubleshooting',
                'category': 'software',
                'solutions': [
                    {'step': 1, 'action': 'Check internet connectivity', 'detail': 'Ensure you have a stable internet connection before troubleshooting email.'},
                    {'step': 2, 'action': 'Verify email server status', 'detail': 'Check if the email service (Exchange, Gmail, etc.) is experiencing an outage.'},
                    {'step': 3, 'action': 'Clear Outlook cache', 'detail': 'Close Outlook, delete files in %localappdata%\\Microsoft\\Outlook\\RoamCache\\'},
                    {'step': 4, 'action': 'Repair Outlook profile', 'detail': 'Control Panel > Mail > Show Profiles > Properties > Repair'},
                    {'step': 5, 'action': 'Check attachment size limits', 'detail': 'Most email servers limit attachments to 25MB. Use OneDrive/SharePoint for larger files.'},
                ]
            },
            'printer_issues': {
                'keywords': ['printer', 'print', 'printing', 'cannot print', 'printer offline', 'paper jam', 'spooler'],
                'title': 'Printer & Printing Issues',
                'category': 'hardware',
                'solutions': [
                    {'step': 1, 'action': 'Check printer power and connections', 'detail': 'Ensure the printer is powered on and connected via USB or network.'},
                    {'step': 2, 'action': 'Set as default printer', 'detail': 'Windows: Settings > Printers & Scanners > Select printer > Set as default.'},
                    {'step': 3, 'action': 'Restart Print Spooler service', 'detail': 'Open Services (services.msc), find Print Spooler, click Restart.'},
                    {'step': 4, 'action': 'Clear print queue', 'detail': 'Stop Print Spooler, delete files in C:\\Windows\\System32\\spool\\PRINTERS\\, restart spooler.'},
                    {'step': 5, 'action': 'Reinstall printer driver', 'detail': 'Remove printer from Settings, download latest driver from manufacturer website, reinstall.'},
                ]
            },
            'blue_screen': {
                'keywords': ['blue screen', 'bsod', 'crash', 'system crash', 'blue screen of death', 'stop error', 'critical error'],
                'title': 'Blue Screen of Death (BSOD) Resolution',
                'category': 'hardware',
                'solutions': [
                    {'step': 1, 'action': 'Note the error code', 'detail': 'Write down the STOP code (e.g., IRQL_NOT_LESS_OR_EQUAL, CRITICAL_PROCESS_DIED).'},
                    {'step': 2, 'action': 'Boot into Safe Mode', 'detail': 'Hold Shift while clicking Restart, then Troubleshoot > Advanced > Startup Settings > Safe Mode.'},
                    {'step': 3, 'action': 'Check for recent changes', 'detail': 'Uninstall recently installed software or drivers that may have caused the crash.'},
                    {'step': 4, 'action': 'Run System File Checker', 'detail': 'Open CMD as admin, run: sfc /scannow'},
                    {'step': 5, 'action': 'Check for hardware issues', 'detail': 'Run Windows Memory Diagnostic (mdsched.exe) and check hard drive health with chkdsk /f'},
                    {'step': 6, 'action': 'Update Windows and drivers', 'detail': 'Install all pending Windows updates and update GPU, network, and chipset drivers.'},
                ]
            },
            'slow_computer': {
                'keywords': ['slow', 'computer slow', 'laptop slow', 'performance', 'lag', 'freezing', 'hanging', 'unresponsive', 'speed'],
                'title': 'Slow Computer Performance',
                'category': 'software',
                'solutions': [
                    {'step': 1, 'action': 'Check Task Manager for resource usage', 'detail': 'Ctrl+Shift+Esc > Performance tab. Look for CPU, Memory, or Disk at 100%.'},
                    {'step': 2, 'action': 'Close unnecessary applications', 'detail': 'End resource-heavy processes in Task Manager > Processes tab.'},
                    {'step': 3, 'action': 'Disable startup programs', 'detail': 'Task Manager > Startup tab > Disable unnecessary items.'},
                    {'step': 4, 'action': 'Run Disk Cleanup', 'detail': 'Search for Disk Cleanup, select drive, check all boxes, and clean.'},
                    {'step': 5, 'action': 'Check for malware', 'detail': 'Run a full scan with Windows Defender or your antivirus software.'},
                    {'step': 6, 'action': 'Consider hardware upgrades', 'detail': 'Adding RAM or switching to an SSD can dramatically improve performance.'},
                ]
            },
            'software_installation': {
                'keywords': ['install', 'installation', 'software install', 'cannot install', 'setup failed', 'installation error', 'permission denied', 'admin rights'],
                'title': 'Software Installation Issues',
                'category': 'software',
                'solutions': [
                    {'step': 1, 'action': 'Check system requirements', 'detail': 'Verify your system meets the minimum requirements for the software.'},
                    {'step': 2, 'action': 'Run installer as administrator', 'detail': 'Right-click the installer > Run as administrator.'},
                    {'step': 3, 'action': 'Disable antivirus temporarily', 'detail': 'Some antivirus software blocks installations. Temporarily disable and retry.'},
                    {'step': 4, 'action': 'Check disk space', 'detail': 'Ensure you have enough free disk space for the installation.'},
                    {'step': 5, 'action': 'Clean previous installation remnants', 'detail': 'Uninstall any previous versions, delete leftover folders, and clear registry entries.'},
                ]
            },
            'security_threat': {
                'keywords': ['virus', 'malware', 'phishing', 'suspicious', 'hacked', 'ransomware', 'security breach', 'suspicious email', 'threat'],
                'title': 'Security Threat Response',
                'category': 'security',
                'solutions': [
                    {'step': 1, 'action': 'Disconnect from the network immediately', 'detail': 'Unplug ethernet cable or disable WiFi to prevent further spread.'},
                    {'step': 2, 'action': 'Do NOT click any suspicious links or attachments', 'detail': 'If you received a phishing email, do not interact with it further.'},
                    {'step': 3, 'action': 'Run a full antivirus scan', 'detail': 'Use Windows Defender or enterprise antivirus to perform a full system scan.'},
                    {'step': 4, 'action': 'Change your passwords immediately', 'detail': 'Change passwords for all accounts, especially email and banking.'},
                    {'step': 5, 'action': 'Report to IT Security team', 'detail': 'Forward suspicious emails to security@company.com and file an incident report.'},
                    {'step': 6, 'action': 'Enable 2FA on all accounts', 'detail': 'Set up two-factor authentication for an extra layer of security.'},
                ]
            },
            'disk_space': {
                'keywords': ['disk space', 'storage full', 'no space', 'hard drive full', 'disk full', 'low disk space', 'c drive full', 'storage'],
                'title': 'Low Disk Space Resolution',
                'category': 'hardware',
                'solutions': [
                    {'step': 1, 'action': 'Run Disk Cleanup utility', 'detail': 'Search "Disk Cleanup", select C: drive, check all categories, click Clean up.'},
                    {'step': 2, 'action': 'Empty Recycle Bin', 'detail': 'Right-click Recycle Bin on desktop > Empty Recycle Bin.'},
                    {'step': 3, 'action': 'Uninstall unused programs', 'detail': 'Settings > Apps > Sort by size > Uninstall programs you no longer need.'},
                    {'step': 4, 'action': 'Move files to cloud storage', 'detail': 'Move large files to OneDrive, Google Drive, or external storage.'},
                    {'step': 5, 'action': 'Clear browser cache', 'detail': 'Chrome: Settings > Privacy > Clear browsing data. Select "Cached images and files".'},
                ]
            },
            'teams_issues': {
                'keywords': ['teams', 'microsoft teams', 'audio not working', 'video freezing', 'cannot join meetings', 'screen share fails'],
                'title': 'Microsoft Teams Issues',
                'category': 'software',
                'solutions': [
                    {'step': 1, 'action': 'Check internet connection', 'detail': 'A stable connection is required for audio and video calls.'},
                    {'step': 2, 'action': 'Verify device settings in Teams', 'detail': 'Go to Settings > Devices and ensure the correct microphone and camera are selected.'},
                    {'step': 3, 'action': 'Clear Teams cache', 'detail': 'Close Teams, delete files in %appdata%\\Microsoft\\Teams, and restart.'},
                    {'step': 4, 'action': 'Update Teams', 'detail': 'Check for updates by clicking your profile picture and selecting Check for updates.'},
                    {'step': 5, 'action': 'Use the web version', 'detail': 'If the desktop app fails, try using Teams in a web browser as a workaround.'},
                ]
            },
            'browser_issues': {
                'keywords': ['browser', 'chrome', 'edge', 'crashes', 'pages not loading', 'too many tabs', 'browser hijacked', 'clearing cache'],
                'title': 'Browser Troubleshooting',
                'category': 'software',
                'solutions': [
                    {'step': 1, 'action': 'Clear browser cache and cookies', 'detail': 'Press Ctrl+Shift+Del and clear cached images and cookies.'},
                    {'step': 2, 'action': 'Disable extensions', 'detail': 'Turn off extensions one by one to see if any are causing the issue.'},
                    {'step': 3, 'action': 'Update your browser', 'detail': 'Ensure you are using the latest version of your web browser.'},
                    {'step': 4, 'action': 'Reset browser settings', 'detail': 'Restore settings to their original defaults in the browser settings menu.'},
                    {'step': 5, 'action': 'Check for malware', 'detail': 'Run a security scan as malware can sometimes hijack browsers.'},
                ]
            },
            'windows_update': {
                'keywords': ['windows update', 'updates stuck', 'update failed', 'restart loop', 'disk space for updates'],
                'title': 'Windows Update Problems',
                'category': 'software',
                'solutions': [
                    {'step': 1, 'action': 'Run the Windows Update Troubleshooter', 'detail': 'Go to Settings > Update & Security > Troubleshoot > Windows Update.'},
                    {'step': 2, 'action': 'Check for sufficient disk space', 'detail': 'Ensure you have enough free space on your C: drive for the update.'},
                    {'step': 3, 'action': 'Restart Windows Update services', 'detail': 'Open Services (services.msc), restart Background Intelligent Transfer Service and Windows Update.'},
                    {'step': 4, 'action': 'Clear the SoftwareDistribution folder', 'detail': 'Stop the update service, delete files in C:\\Windows\\SoftwareDistribution, and restart the service.'},
                    {'step': 5, 'action': 'Install updates manually', 'detail': 'Download the specific update from the Microsoft Update Catalog and install it manually.'},
                ]
            },
            'remote_desktop': {
                'keywords': ['remote desktop', 'rdp', 'cannot connect', 'black screen', 'slow performance', 'authentication error'],
                'title': 'Remote Desktop Connection Issues',
                'category': 'network',
                'solutions': [
                    {'step': 1, 'action': 'Verify target PC is awake', 'detail': 'Ensure the remote computer is turned on and not in sleep or hibernation mode.'},
                    {'step': 2, 'action': 'Check network connection', 'detail': 'Ensure both the local and remote computers have active internet connections.'},
                    {'step': 3, 'action': 'Verify Remote Desktop is enabled', 'detail': 'On the remote PC, go to Settings > System > Remote Desktop and ensure it is turned on.'},
                    {'step': 4, 'action': 'Check firewall settings', 'detail': 'Ensure Remote Desktop is allowed through the Windows Firewall on the remote PC.'},
                    {'step': 5, 'action': 'Verify credentials', 'detail': 'Ensure you are using the correct username and password, including the domain if applicable.'},
                ]
            },
            'data_backup': {
                'keywords': ['backup', 'data backup', 'recovery', 'files accidentally deleted', 'backup failed', 'restore from backup', 'cloud sync issues'],
                'title': 'Data Backup and Recovery',
                'category': 'software',
                'solutions': [
                    {'step': 1, 'action': 'Check the Recycle Bin', 'detail': 'If a file was recently deleted, it might still be in the Recycle Bin.'},
                    {'step': 2, 'action': 'Verify backup service status', 'detail': 'Check if your backup software (e.g., OneDrive, File History) is running and synced.'},
                    {'step': 3, 'action': 'Check storage space for backups', 'detail': 'Ensure the destination drive or cloud storage has enough space for the backup.'},
                    {'step': 4, 'action': 'Restore from a previous version', 'detail': 'Right-click the folder where the file was > Restore previous versions.'},
                    {'step': 5, 'action': 'Contact IT for enterprise recovery', 'detail': 'If using enterprise network drives, IT may have snapshot backups to restore from.'},
                ]
            },
        }
    
    def search(self, query):
        """Search knowledge base using keyword matching and similarity scoring."""
        query_lower = query.lower()
        results = []
        
        for key, article in self.knowledge_base.items():
            score = 0
            # Keyword matching
            for keyword in article['keywords']:
                if keyword in query_lower:
                    score += 10
                elif any(word in keyword for word in query_lower.split()):
                    score += 3
            
            # Title similarity
            title_similarity = SequenceMatcher(None, query_lower, article['title'].lower()).ratio()
            score += title_similarity * 5
            
            if score > 0:
                results.append({
                    'key': key,
                    'title': article['title'],
                    'category': article['category'],
                    'score': round(score, 2),
                    'solutions': article['solutions'],
                    'confidence': min(score / 15, 1.0),
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:3]  # Top 3 results
    
    def get_response(self, query):
        """Generate a troubleshooting response for a user query."""
        results = self.search(query)
        
        if not results:
            return {
                'message': "I couldn't find a specific solution in my knowledge base for your issue. Here are some general steps you can try:\n\n1. **Restart your device** — This resolves ~30% of common IT issues\n2. **Check for updates** — Ensure your OS and software are up to date\n3. **Search the Knowledge Base** — Browse our articles for related topics\n4. **Create a support ticket** — Our team will investigate your issue\n\nCould you provide more details about your problem?",
                'confidence': 0.2,
                'sources': [],
                'category': 'general',
            }
        
        best = results[0]
        steps_text = '\n'.join([
            f"**Step {s['step']}: {s['action']}**\n{s['detail']}"
            for s in best['solutions']
        ])
        
        message = f"Based on your description, this appears to be related to **{best['title']}**.\n\nHere's a step-by-step troubleshooting guide:\n\n{steps_text}"
        
        if len(results) > 1:
            related = ', '.join([r['title'] for r in results[1:]])
            message += f"\n\n---\n💡 **Related topics:** {related}"
        
        return {
            'message': message,
            'confidence': round(best['confidence'], 2),
            'sources': [r['title'] for r in results],
            'category': best['category'],
        }
    
    def classify_ticket(self, title, description):
        """Classify a ticket's category, priority, and sentiment."""
        text = f"{title} {description}".lower()
        
        # Category classification
        category_keywords = {
            'hardware': ['printer', 'monitor', 'keyboard', 'mouse', 'laptop', 'desktop', 'hardware', 'screen', 'battery', 'charger', 'usb', 'disk', 'drive', 'memory', 'ram', 'blue screen', 'bsod', 'power'],
            'software': ['install', 'update', 'software', 'application', 'app', 'crash', 'error', 'bug', 'slow', 'freeze', 'outlook', 'excel', 'word', 'teams', 'zoom', 'browser', 'chrome'],
            'network': ['network', 'internet', 'wifi', 'ethernet', 'vpn', 'dns', 'ip address', 'connectivity', 'connection', 'firewall', 'proxy', 'bandwidth', 'latency'],
            'security': ['virus', 'malware', 'phishing', 'security', 'breach', 'hack', 'ransomware', 'suspicious', 'threat', 'unauthorized', 'spam', 'scam'],
            'access': ['password', 'login', 'access', 'permission', 'locked', 'account', 'authentication', 'sso', 'mfa', '2fa', 'role', 'privilege'],
        }
        
        category_scores = {}
        for cat, keywords in category_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                category_scores[cat] = score
        
        category = max(category_scores, key=category_scores.get) if category_scores else 'other'
        
        # Priority classification
        critical_words = ['urgent', 'critical', 'emergency', 'down', 'outage', 'all users', 'production', 'server down', 'cannot work', 'blocked']
        high_words = ['important', 'asap', 'affecting multiple', 'deadline', 'broken', 'not working']
        low_words = ['when possible', 'minor', 'cosmetic', 'nice to have', 'feature request', 'suggestion']
        
        if any(w in text for w in critical_words):
            priority = 'critical'
        elif any(w in text for w in high_words):
            priority = 'high'
        elif any(w in text for w in low_words):
            priority = 'low'
        else:
            priority = 'medium'
        
        # Sentiment analysis
        frustrated_words = ['frustrated', 'angry', 'furious', 'unacceptable', 'terrible', 'worst', 'hate', 'ridiculous', 'waste of time', 'incompetent', 'useless', 'annoying', 'fed up']
        negative_words = ['problem', 'issue', 'bug', 'error', 'fail', 'broken', 'wrong', 'bad', 'poor', 'disappointed']
        positive_words = ['please', 'thank', 'appreciate', 'help', 'kind', 'great', 'good', 'wonderful']
        
        if any(w in text for w in frustrated_words):
            sentiment = 'frustrated'
        elif sum(1 for w in negative_words if w in text) > 2:
            sentiment = 'negative'
        elif any(w in text for w in positive_words):
            sentiment = 'positive'
        else:
            sentiment = 'neutral'
        
        # Get AI suggestion
        ai_response = self.get_response(f"{title} {description}")
        
        return {
            'category': category,
            'priority': priority,
            'sentiment': sentiment,
            'ai_suggestion': ai_response['message'],
            'confidence': ai_response['confidence'],
        }
    
    def analyze_logs(self, log_content):
        """Analyze log content for errors, warnings, and anomalies."""
        lines = log_content.strip().split('\n')
        errors = []
        warnings = []
        info = []
        anomalies = []
        
        error_patterns = [
            (r'(?i)\b(error|err|fatal|critical|exception|traceback|failed|failure)\b', 'error'),
            (r'(?i)\b(warning|warn|caution|deprecated)\b', 'warning'),
            (r'(?i)\b(denied|unauthorized|forbidden|403|401|500|503|timeout|refused)\b', 'error'),
        ]
        
        for i, line in enumerate(lines, 1):
            line_type = 'info'
            for pattern, level in error_patterns:
                if re.search(pattern, line):
                    line_type = level
                    break
            
            entry = {'line': i, 'content': line.strip(), 'type': line_type}
            
            if line_type == 'error':
                errors.append(entry)
            elif line_type == 'warning':
                warnings.append(entry)
            else:
                info.append(entry)
        
        # Detect anomalies (repeated errors, patterns)
        error_messages = [e['content'] for e in errors]
        from collections import Counter
        error_counts = Counter(error_messages)
        for msg, count in error_counts.items():
            if count >= 2:
                anomalies.append({
                    'type': 'Repeated Error',
                    'message': msg,
                    'count': count,
                    'severity': 'high' if count >= 5 else 'medium',
                    'recommendation': f'This error occurred {count} times. Investigate root cause immediately.' if count >= 5 else f'This error occurred {count} times. Monitor and investigate.'
                })
        
        # Check for rapid succession errors
        if len(errors) > len(lines) * 0.3:
            anomalies.append({
                'type': 'High Error Rate',
                'message': f'{len(errors)} errors found in {len(lines)} lines ({round(len(errors)/len(lines)*100, 1)}% error rate)',
                'count': len(errors),
                'severity': 'critical',
                'recommendation': 'Error rate exceeds 30%. System may be in a failure state. Immediate attention required.'
            })
        
        summary = {
            'total_lines': len(lines),
            'errors': len(errors),
            'warnings': len(warnings),
            'info': len(info),
            'anomaly_count': len(anomalies),
            'health_score': max(0, 100 - (len(errors) * 5) - (len(warnings) * 2)),
        }
        
        return {
            'summary': summary,
            'errors': errors[:50],  # Limit output
            'warnings': warnings[:50],
            'anomalies': anomalies,
            'all_lines': [{'line': i+1, 'content': l.strip(), 'type': 'error' if any(l.strip() == e['content'] for e in errors) else ('warning' if any(l.strip() == w['content'] for w in warnings) else 'info')} for i, l in enumerate(lines)][:200],
        }

# Singleton instance
ai_engine = TroubleshootAI()
