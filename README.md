#JobPulse

A comprehensive, multi-source job hunting automation platform that discovers opportunities and manages outreach campaigns.

## Features

### 🎯 Multi-Source Job Discovery
- **Reddit**: Monitors r/forhire, r/freelance, r/remotework, r/jobsearch, r/hiring, r/startups
- **GitHub**: Scans repository issues for hiring posts
- **HackerNews**: Processes "Who is Hiring" threads
- **AngelList**: Startup job opportunities
- **Discord**: Real-time job monitoring in servers

### 🏢 Company Discovery & Direct Outreach
- **Y Combinator**: Startup directory scraping
- **GitHub Trending**: Active tech companies
- **Curated Tech Companies**: Established companies database
- **Automatic Email Discovery**: Generates potential contact emails
- **Domain Resolution**: Company website discovery

### 📧 Smart Email Management
- **Intelligent Templates**: Job applications vs. company outreach
- **Rate Limiting**: Respects daily email limits
- **Success Tracking**: Detailed statistics and failure analysis
- **Duplicate Prevention**: URL-based deduplication
- **Professional Formatting**: Clean, non-AI-generated messaging

### 📊 Advanced Analytics
- **Real-time Statistics**: Lead tracking, email success rates
- **Platform Breakdown**: Source performance analysis
- **CSV Export**: Backup and analysis capabilities
- **Google Sheets Integration**: Centralized lead management

## Quick Start

1. **Install Dependencies**
   ```bash
   cd automate
   pip install -r requirements.txt
   ```

2. **Configure Settings**
   Edit `config.py` with your credentials:
   - Discord bot token
   - GitHub personal access token
   - Gmail app password
   - Google Sheets credentials

3. **Run the System**
   ```bash
   python main.py
   ```

## Configuration

### Email Setup
1. Enable 2FA on Gmail
2. Generate App Password
3. Update `EMAIL_CONFIG` in config.py

### Discord Setup
1. Create bot at discord.com/developers/applications
2. Enable Message Content Intent
3. Add bot to job-hunting servers

### Google Sheets Setup
1. Create Google Cloud project
2. Enable Sheets and Drive APIs
3. Create service account
4. Download credentials JSON

## Automation Schedule

- **Job Scanning**: Every 2 hours
- **Company Discovery**: Every 12 hours  
- **Email Outreach**: Every 8 hours
- **Statistics**: Every hour
- **Data Backup**: Daily at 23:59

## Architecture

```
automate/
├── main.py              # Main application entry point
├── config.py            # Configuration management
├── job_sources.py       # Multi-platform job scrapers
├── company_finder.py    # Company discovery system
├── email_manager.py     # Email automation
├── data_manager.py      # Data persistence & deduplication
├── discord_monitor.py   # Real-time Discord monitoring
└── requirements.txt     # Dependencies
```

## Output Files

- `leads_YYYY-MM.csv` - Monthly job leads
- `companies_YYYY-MM.csv` - Discovered companies
- `job_data.json` - Complete data backup
- `email_stats.json` - Email performance metrics

## Advanced Features

### Multi-Client Support
The system is designed to handle multiple job seekers:
- Separate configuration profiles
- Independent email limits
- Isolated data tracking

### Professional Messaging
- Natural language templates
- Personalized outreach
- No AI-generated markers
- Industry-appropriate tone

### Scalable Architecture
- Modular design
- Easy source addition
- Configurable rate limits
- Error handling & recovery

## Best Practices

1. **Email Limits**: Stay under 25 emails/day
2. **Rate Limiting**: Built-in delays prevent blocking
3. **Quality Control**: Filter ensures relevant opportunities
4. **Data Backup**: Regular persistence prevents data loss
5. **Monitoring**: Real-time statistics track performance

## Troubleshooting

### Common Issues
- **Discord Intents**: Enable Message Content Intent in developer portal
- **Google Sheets**: Verify API access and service account permissions
- **Email Limits**: Monitor daily quota usage
- **Rate Limiting**: Built-in delays prevent API blocking

### Support
Check logs for error details and verify all API credentials are current.
