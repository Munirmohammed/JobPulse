import requests
import time
import asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re

class JobScraper:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def is_recent_post(self, created_date, max_days=30):
        if isinstance(created_date, str):
            try:
                created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            except:
                return True
        
        if isinstance(created_date, (int, float)):
            created_date = datetime.fromtimestamp(created_date)
        
        return (datetime.now() - created_date.replace(tzinfo=None)).days <= max_days

    def filter_hiring_post(self, title, content=""):
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Skip job seekers
        skip_phrases = ['for hire', 'looking for work', 'seeking employment', 'available for']
        if any(phrase in title_lower for phrase in skip_phrases):
            return False
        
        # Must have hiring indicators
        hiring_indicators = ['hiring', 'looking for', 'seeking', 'need', 'wanted', 'join our team', 'we are hiring']
        has_hiring = any(indicator in title_lower or indicator in content_lower for indicator in hiring_indicators)
        
        # Must have relevant keywords
        has_keywords = any(keyword in title_lower or keyword in content_lower for keyword in self.config.keywords)
        
        return has_hiring and has_keywords

class RedditScraper(JobScraper):
    def get_jobs(self):
        jobs = []
        subreddits = ['forhire', 'freelance', 'remotework', 'jobsearch', 'hiring', 'startups']
        
        for subreddit in subreddits:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=50"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    for post in data['data']['children']:
                        post_data = post['data']
                        
                        if (self.is_recent_post(post_data['created_utc']) and 
                            self.filter_hiring_post(post_data['title'], post_data.get('selftext', ''))):
                            
                            jobs.append({
                                'platform': 'Reddit',
                                'source': f"r/{subreddit}",
                                'title': post_data['title'],
                                'author': post_data['author'],
                                'content': post_data.get('selftext', '')[:500],
                                'url': f"https://reddit.com{post_data['permalink']}",
                                'created_at': datetime.fromtimestamp(post_data['created_utc']).isoformat()
                            })
                
                time.sleep(2)
            except Exception as e:
                print(f"Reddit error for r/{subreddit}: {e}")
        
        return jobs

class GitHubScraper(JobScraper):
    def get_jobs(self):
        jobs = []
        queries = [
            'hiring backend developer',
            'looking for node.js developer', 
            'remote software engineer',
            'full stack developer position',
            'python developer job'
        ]
        
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.config.github_token:
            headers['Authorization'] = f"token {self.config.github_token}"
        
        for query in queries:
            try:
                url = f"https://api.github.com/search/issues?q={query}&sort=created&order=desc&per_page=30"
                response = self.session.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data['items']:
                        if (self.is_recent_post(item['created_at']) and 
                            self.filter_hiring_post(item['title'], item.get('body', ''))):
                            
                            jobs.append({
                                'platform': 'GitHub',
                                'source': item.get('repository_url', 'Unknown').split('/')[-1],
                                'title': item['title'],
                                'author': item['user']['login'],
                                'content': (item.get('body') or '')[:500],
                                'url': item['html_url'],
                                'created_at': item['created_at']
                            })
                
                time.sleep(1)
            except Exception as e:
                print(f"GitHub error for query '{query}': {e}")
        
        return jobs

class HackerNewsScraper(JobScraper):
    def get_jobs(self):
        jobs = []
        try:
            # Get "Who is hiring" posts
            url = "https://hacker-news.firebaseio.com/v0/item/39217901.json"  # Latest who is hiring
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'kids' in data:
                    for kid_id in data['kids'][:50]:  # Limit to first 50 comments
                        try:
                            comment_url = f"https://hacker-news.firebaseio.com/v0/item/{kid_id}.json"
                            comment_response = self.session.get(comment_url)
                            
                            if comment_response.status_code == 200:
                                comment_data = comment_response.json()
                                comment_text = comment_data.get('text', '')
                                
                                if self.filter_hiring_post(comment_text):
                                    jobs.append({
                                        'platform': 'HackerNews',
                                        'source': 'Who is Hiring',
                                        'title': 'HN Job Post',
                                        'author': comment_data.get('by', 'Unknown'),
                                        'content': comment_text[:500],
                                        'url': f"https://news.ycombinator.com/item?id={kid_id}",
                                        'created_at': datetime.fromtimestamp(comment_data.get('time', 0)).isoformat()
                                    })
                            
                            time.sleep(0.5)
                        except:
                            continue
        except Exception as e:
            print(f"HackerNews error: {e}")
        
        return jobs

class AngelListScraper(JobScraper):
    def get_jobs(self):
        jobs = []
        try:
            # AngelList job search (simplified)
            search_terms = ['backend', 'frontend', 'fullstack', 'python', 'javascript']
            
            for term in search_terms:
                url = f"https://angel.co/jobs?keywords={term}&remote=true"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Parse job listings (this would need to be updated based on current AngelList structure)
                    job_cards = soup.find_all('div', class_='job-card')  # Example selector
                    
                    for card in job_cards[:10]:
                        try:
                            title_elem = card.find('h3')
                            company_elem = card.find('h4')
                            
                            if title_elem and company_elem:
                                jobs.append({
                                    'platform': 'AngelList',
                                    'source': company_elem.text.strip(),
                                    'title': title_elem.text.strip(),
                                    'author': company_elem.text.strip(),
                                    'content': 'Remote job opportunity',
                                    'url': f"https://angel.co/jobs/{term}",
                                    'created_at': datetime.now().isoformat()
                                })
                        except:
                            continue
                
                time.sleep(2)
        except Exception as e:
            print(f"AngelList error: {e}")
        
        return jobs

class JobAggregator:
    def __init__(self, config):
        self.config = config
        self.scrapers = [
            RedditScraper(config),
            GitHubScraper(config),
            HackerNewsScraper(config),
            AngelListScraper(config)
        ]
    
    def get_all_jobs(self):
        all_jobs = []
        
        for scraper in self.scrapers:
            try:
                jobs = scraper.get_jobs()
                all_jobs.extend(jobs)
                print(f"Found {len(jobs)} jobs from {scraper.__class__.__name__}")
            except Exception as e:
                print(f"Error in {scraper.__class__.__name__}: {e}")
        
        return all_jobs
