import json
import csv
from datetime import datetime
from typing import List, Dict, Set
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class LeadManager:
    def __init__(self, config):
        self.config = config
        self.leads: List[Dict] = []
        self.seen_urls: Set[str] = set()
        self.companies: List[Dict] = []
        self.sheet = None
        self.setup_sheets()

    def setup_sheets(self):
        try:
            if self.config.google_sheets_creds:
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    self.config.google_sheets_creds, scope
                )
                gc = gspread.authorize(creds)
                self.sheet = gc.open(self.config.sheet_name).sheet1
                print("✓ Google Sheets connected")
        except Exception as e:
            print(f"⚠ Google Sheets setup failed: {e}")

    def is_duplicate(self, url: str) -> bool:
        return url in self.seen_urls

    def add_lead(self, lead_data: Dict) -> bool:
        if self.is_duplicate(lead_data['url']):
            return False
        
        lead_data['timestamp'] = datetime.now().isoformat()
        lead_data['status'] = 'new'
        lead_data['id'] = len(self.leads) + 1
        
        self.leads.append(lead_data)
        self.seen_urls.add(lead_data['url'])
        
        self.save_to_csv(lead_data)
        self.save_to_sheets(lead_data)
        
        return True

    def add_company(self, company_data: Dict) -> bool:
        company_data['discovered_at'] = datetime.now().isoformat()
        company_data['status'] = 'new'
        company_data['id'] = len(self.companies) + 1
        
        self.companies.append(company_data)
        self.save_company_to_csv(company_data)
        
        return True

    def save_to_csv(self, lead: Dict):
        filename = f"leads_{datetime.now().strftime('%Y-%m')}.csv"
        
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as file:
                if file.tell() == 0:
                    writer = csv.DictWriter(file, fieldnames=lead.keys())
                    writer.writeheader()
                else:
                    writer = csv.DictWriter(file, fieldnames=lead.keys())
                writer.writerow(lead)
        except Exception as e:
            print(f"CSV save error: {e}")

    def save_company_to_csv(self, company: Dict):
        filename = f"companies_{datetime.now().strftime('%Y-%m')}.csv"
        
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as file:
                if file.tell() == 0:
                    writer = csv.DictWriter(file, fieldnames=company.keys())
                    writer.writeheader()
                else:
                    writer = csv.DictWriter(file, fieldnames=company.keys())
                writer.writerow(company)
        except Exception as e:
            print(f"Company CSV save error: {e}")

    def save_to_sheets(self, lead: Dict):
        if not self.sheet:
            return
            
        try:
            row = [
                lead.get('platform', ''),
                lead.get('source', ''),
                lead.get('title', ''),
                lead.get('author', ''),
                lead.get('content', '')[:100],
                lead.get('url', ''),
                lead.get('timestamp', ''),
                lead.get('status', '')
            ]
            self.sheet.append_row(row)
        except Exception as e:
            print(f"Sheets save error: {e}")

    def get_new_leads(self) -> List[Dict]:
        return [lead for lead in self.leads if lead['status'] == 'new']

    def get_companies_for_outreach(self) -> List[Dict]:
        return [company for company in self.companies 
                if company['status'] == 'new' and 'real_emails' in company and company['real_emails']]

    def mark_lead_contacted(self, lead_id: int, email: str):
        for lead in self.leads:
            if lead['id'] == lead_id:
                lead['status'] = 'contacted'
                lead['contacted_email'] = email
                lead['contacted_at'] = datetime.now().isoformat()
                break

    def mark_company_contacted(self, company_id: int, email: str):
        for company in self.companies:
            if company['id'] == company_id:
                company['status'] = 'contacted'
                company['contacted_email'] = email
                company['contacted_at'] = datetime.now().isoformat()
                break

    def get_statistics(self) -> Dict:
        total_leads = len(self.leads)
        new_leads = len([l for l in self.leads if l['status'] == 'new'])
        contacted_leads = len([l for l in self.leads if l['status'] == 'contacted'])
        
        total_companies = len(self.companies)
        new_companies = len([c for c in self.companies if c['status'] == 'new'])
        contacted_companies = len([c for c in self.companies if c['status'] == 'contacted'])
        
        platform_breakdown = {}
        for lead in self.leads:
            platform = lead.get('platform', 'Unknown')
            platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1
        
        return {
            'leads': {
                'total': total_leads,
                'new': new_leads,
                'contacted': contacted_leads,
                'by_platform': platform_breakdown
            },
            'companies': {
                'total': total_companies,
                'new': new_companies,
                'contacted': contacted_companies
            },
            'duplicates_prevented': len(self.seen_urls) - total_leads
        }

    def save_data(self):
        data = {
            'leads': self.leads,
            'companies': self.companies,
            'seen_urls': list(self.seen_urls),
            'saved_at': datetime.now().isoformat()
        }
        
        with open('job_data.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def load_data(self):
        try:
            with open('job_data.json', 'r') as f:
                data = json.load(f)
                self.leads = data.get('leads', [])
                self.companies = data.get('companies', [])
                self.seen_urls = set(data.get('seen_urls', []))
                print(f"Loaded {len(self.leads)} leads and {len(self.companies)} companies")
        except FileNotFoundError:
            print("No previous data found, starting fresh")
