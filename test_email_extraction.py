#!/usr/bin/env python3

"""
Test script to verify real email extraction from company websites
"""

from company_finder import WebsiteEmailExtractor
import time

def test_email_extraction():
    extractor = WebsiteEmailExtractor()
    
    # Test with known companies
    test_companies = [
        "https://stripe.com",
        "https://vercel.com", 
        "https://supabase.com",
        "https://linear.app",
        "https://notion.so"
    ]
    
    print("🧪 Testing Real Email Extraction")
    print("=" * 50)
    
    for i, website in enumerate(test_companies, 1):
        print(f"\n{i}. Testing: {website}")
        print("-" * 30)
        
        try:
            emails = extractor.extract_emails_from_website(website)
            
            if emails:
                print(f"✅ Found {len(emails)} real emails:")
                for email in emails:
                    print(f"   📧 {email}")
            else:
                print("❌ No emails found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(2)  # Be respectful
    
    print(f"\n✅ Test complete!")

if __name__ == "__main__":
    test_email_extraction()
