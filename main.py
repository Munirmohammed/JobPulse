import asyncio
import schedule
import time
import threading
from datetime import datetime
import os

from config import CONFIG, EMAIL_CONFIG, PERSONAL_INFO
from job_sources import JobAggregator
from company_finder import CompanyOutreachManager
from email_manager import EmailSender
from data_manager import LeadManager
from discord_monitor import DiscordJobMonitor
from health_check import start_health_server

class JobHuntingBot:
    def __init__(self):
        self.config = CONFIG
        self.email_config = EMAIL_CONFIG
        self.personal_info = PERSONAL_INFO
        
        self.data_manager = LeadManager(self.config)
        self.job_aggregator = JobAggregator(self.config)
        self.company_manager = CompanyOutreachManager(self.config)
        self.email_sender = EmailSender(self.email_config, self.personal_info)
        self.discord_monitor = DiscordJobMonitor(self.config, self.handle_discord_job)
        
        self.data_manager.load_data()
        self.email_sender.load_stats()

    async def handle_discord_job(self, job_data):
        if self.data_manager.add_lead(job_data):
            print(f"✓ New Discord job: {job_data['title'][:50]}")

    def scan_job_sources(self):
        print(f"\n🔍 Starting job scan at {datetime.now().strftime('%H:%M:%S')}")
        
        jobs = self.job_aggregator.get_all_jobs()
        new_jobs = 0
        
        for job in jobs:
            if self.data_manager.add_lead(job):
                new_jobs += 1
        
        print(f"✓ Job scan complete: {new_jobs} new jobs found")
        self.print_quick_stats()

    def discover_companies(self):
        print(f"\n🏢 Starting company discovery at {datetime.now().strftime('%H:%M:%S')}")
        
        # Find companies from all sources
        companies = self.company_manager.find_all_companies()
        
        # Extract real emails from their websites
        print(f"📧 Extracting real emails from {len(companies)} companies...")
        enriched_companies = self.company_manager.extract_real_emails(companies)
        
        # Filter companies that have real emails
        companies_with_emails = [c for c in enriched_companies if c.get('email_count', 0) > 0]
        
        new_companies = 0
        for company in companies_with_emails:
            if self.data_manager.add_company(company):
                new_companies += 1
        
        total_emails = sum(c.get('email_count', 0) for c in companies_with_emails)
        print(f"✓ Company discovery complete: {new_companies} new companies, {total_emails} real emails found")

    def process_outreach(self):
        print(f"\n📧 Processing outreach at {datetime.now().strftime('%H:%M:%S')}")
        
        # Job applications
        new_leads = self.data_manager.get_new_leads()
        job_emails_sent = 0
        
        for lead in new_leads[:5]:  # Limit to 5 per batch
            if not self.email_sender.can_send_email():
                break
                
            # Extract email from job post or use company domain
            potential_emails = []
            
            # Try to extract emails from content
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            found_emails = re.findall(email_pattern, lead.get('content', ''))
            potential_emails.extend(found_emails)
            
            if potential_emails:
                if self.email_sender.send_job_application(lead, potential_emails[:3]):
                    self.data_manager.mark_lead_contacted(lead['id'], potential_emails[0])
                    job_emails_sent += 1
                    time.sleep(10)
        
        # Company outreach
        companies = self.data_manager.get_companies_for_outreach()
        company_emails_sent = 0
        
        for company in companies[:3]:  # Limit to 3 per batch
            if not self.email_sender.can_send_email():
                break
                
            if 'real_emails' in company and company['real_emails']:
                if self.email_sender.send_company_outreach(company, company['real_emails'][:3]):
                    self.data_manager.mark_company_contacted(company['id'], company['real_emails'][0])
                    company_emails_sent += 1
                    time.sleep(10)
        
        print(f"✓ Outreach complete: {job_emails_sent} job applications, {company_emails_sent} company outreach")
        
        if job_emails_sent + company_emails_sent > 0:
            self.email_sender.save_stats()

    def print_statistics(self):
        print(f"\n📊 Bot Statistics - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        data_stats = self.data_manager.get_statistics()
        email_stats = self.email_sender.get_statistics()
        
        print(f"   📈 Leads: {data_stats['leads']['total']} total, {data_stats['leads']['new']} new")
        print(f"   🏢 Companies: {data_stats['companies']['total']} total, {data_stats['companies']['new']} new")
        print(f"   📧 Emails: {email_stats['emails_sent']} sent, {email_stats['emails_failed']} failed")
        print(f"   🎯 Success Rate: {email_stats['success_rate']:.1f}%")
        print(f"   🔄 Duplicates Prevented: {data_stats['duplicates_prevented']}")
        
        if data_stats['leads']['by_platform']:
            print("   📱 Platform Breakdown:")
            for platform, count in data_stats['leads']['by_platform'].items():
                print(f"      {platform}: {count}")

    def print_quick_stats(self):
        data_stats = self.data_manager.get_statistics()
        print(f"   Total leads: {data_stats['leads']['total']} | New: {data_stats['leads']['new']}")

    def setup_scheduler(self):
        print("⏰ Setting up automation schedule...")
        
        # Job scanning every 2 hours
        schedule.every(2).hours.do(self.scan_job_sources)
        
        # Company discovery twice daily
        schedule.every(12).hours.do(self.discover_companies)
        
        # Process outreach three times daily
        schedule.every(8).hours.do(self.process_outreach)
        
        # Statistics every hour
        schedule.every().hour.do(self.print_statistics)
        
        # Data backup daily
        schedule.every().day.at("23:59").do(self.data_manager.save_data)

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

    async def start_discord_monitor(self):
        if self.config.discord_token:
            await self.discord_monitor.start()
        else:
            print("⚠ No Discord token provided")
            while True:
                await asyncio.sleep(60)

    def run(self):
        print("🚀 JobHuntingBot Starting...")
        print("=" * 50)
        
        # Setup automation
        self.setup_scheduler()
        
        # Start background scheduler
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Run initial scans
        self.scan_job_sources()
        self.discover_companies()
        self.print_statistics()
        
        # Start Discord monitoring
        try:
            asyncio.run(self.start_discord_monitor())
        except KeyboardInterrupt:
            print("\n👋 JobHuntingBot stopped")
            self.cleanup()
        except Exception as e:
            print(f"⚠ Discord failed, continuing without it: {e}")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n👋 JobHuntingBot stopped")
                self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exit"""
        print("🧹 Cleaning up...")
        self.data_manager.save_data()
        self.email_sender.save_stats()
        self.company_manager.close_drivers()
        print("✓ Cleanup complete")

if __name__ == "__main__":
    print("🤖 Starting JobPulse - Automated Job Hunting Bot")
    print("=" * 50)
    
    # Start health check server for deployment monitoring
    health_port = int(os.environ.get('PORT', 8080))
    start_health_server(health_port)
    
    bot = JobHuntingBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 JobPulse stopped by user")
    except Exception as e:
        print(f"\n❌ JobPulse crashed: {e}")
        import traceback
        traceback.print_exc()
