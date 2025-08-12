import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import json

class EmailTemplate:
    @staticmethod
    def job_application(personal_info, job_details):
        subject = f"Backend Engineer Application - {personal_info.name}"
        
        body = f"""Hi,

I came across your job posting for a backend developer position and I'm very interested in joining your team.

I'm a backend engineer with expertise in:
• Node.js, TypeScript, and Python
• REST APIs and microservices architecture  
• Database design (PostgreSQL, MongoDB)
• Cloud platforms (AWS, Docker, Kubernetes)
• Agile development and CI/CD

I've successfully delivered scalable backend solutions for startups and established companies. I'm passionate about writing clean, efficient code and solving complex technical challenges.

I'd love to discuss how I can contribute to your team's success. I'm available for a call at your convenience.

Best regards,
{personal_info.name}
{personal_info.linkedin}
{personal_info.github}

---
Found via: {job_details.get('url', 'Direct outreach')}
"""
        return subject, body

    @staticmethod
    def company_outreach(personal_info, company_info):
        subject = f"Experienced Backend Engineer - {personal_info.name}"
        
        body = f"""Hello,

I hope this message finds you well. I'm reaching out because I'm impressed with {company_info.get('name', 'your company')}'s work in {company_info.get('type', 'technology')}.

As a backend engineer with 5+ years of experience, I specialize in:
• Scalable API development (Node.js, Python)
• Cloud architecture and deployment
• Database optimization and design
• Team collaboration and code review

I'm particularly interested in {company_info.get('description', 'innovative technology solutions')} and would love to explore opportunities to contribute to your engineering team.

Would you be open to a brief conversation about potential openings or future opportunities?

Thank you for your time.

Best regards,
{personal_info.name}
{personal_info.linkedin}
{personal_info.github}
"""
        return subject, body

class EmailSender:
    def __init__(self, email_config, personal_info):
        self.config = email_config
        self.personal_info = personal_info
        self.stats = {
            'sent': 0,
            'failed': 0,
            'daily_count': 0,
            'last_reset': datetime.now().date(),
            'attempts': []
        }

    def reset_daily_count(self):
        today = datetime.now().date()
        if today != self.stats['last_reset']:
            self.stats['daily_count'] = 0
            self.stats['last_reset'] = today

    def can_send_email(self, daily_limit=25):
        self.reset_daily_count()
        return self.stats['daily_count'] < daily_limit

    def send_email(self, to_email: str, subject: str, body: str, context: Dict = None):
        if not self.can_send_email():
            print(f"Daily email limit reached ({self.stats['daily_count']})")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.address
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.address, self.config.password)
            
            text = msg.as_string()
            server.sendmail(self.config.address, to_email, text)
            server.quit()

            self.stats['sent'] += 1
            self.stats['daily_count'] += 1
            
            attempt_record = {
                'email': to_email,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }
            self.stats['attempts'].append(attempt_record)
            
            print(f"✓ Email sent to {to_email}")
            return True

        except Exception as e:
            self.stats['failed'] += 1
            
            attempt_record = {
                'email': to_email,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }
            self.stats['attempts'].append(attempt_record)
            
            print(f"✗ Failed to send to {to_email}: {e}")
            return False

    def send_job_application(self, job_details: Dict, email_list: List[str]):
        subject, body = EmailTemplate.job_application(self.personal_info, job_details)
        
        for email in email_list:
            if self.send_email(email, subject, body, {'type': 'job_application', 'job': job_details}):
                time.sleep(5)  # Delay between emails
                return True
        return False

    def send_company_outreach(self, company_info: Dict, email_list: List[str]):
        subject, body = EmailTemplate.company_outreach(self.personal_info, company_info)
        
        for email in email_list:
            if self.send_email(email, subject, body, {'type': 'company_outreach', 'company': company_info}):
                time.sleep(5)
                return True
        return False

    def get_statistics(self):
        success_rate = 0
        if self.stats['sent'] + self.stats['failed'] > 0:
            success_rate = (self.stats['sent'] / (self.stats['sent'] + self.stats['failed'])) * 100
        
        return {
            'emails_sent': self.stats['sent'],
            'emails_failed': self.stats['failed'],
            'daily_count': self.stats['daily_count'],
            'success_rate': success_rate,
            'recent_attempts': self.stats['attempts'][-10:]  # Last 10 attempts
        }

    def save_stats(self, filename='email_stats.json'):
        with open(filename, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)

    def load_stats(self, filename='email_stats.json'):
        try:
            with open(filename, 'r') as f:
                self.stats.update(json.load(f))
        except FileNotFoundError:
            pass
