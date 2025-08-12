import discord
import asyncio
from datetime import datetime
from typing import Callable, Dict

class DiscordJobMonitor:
    def __init__(self, config, on_job_found: Callable):
        self.config = config
        self.on_job_found = on_job_found
        self.client = None
        self.setup_client()

    def setup_client(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        self.client = discord.Client(intents=intents)
        
        @self.client.event
        async def on_ready():
            print(f"✓ Discord monitor active as {self.client.user}")
            
        @self.client.event
        async def on_message(message):
            await self.process_message(message)

    async def process_message(self, message):
        if message.author.bot:
            return
            
        content = message.content.lower()
        
        # Check for job-related keywords
        job_indicators = ['hiring', 'looking for', 'need', 'seeking', 'job', 'position']
        tech_keywords = self.config.keywords
        
        has_job_indicator = any(indicator in content for indicator in job_indicators)
        has_tech_keyword = any(keyword in content for keyword in tech_keywords)
        
        if has_job_indicator and has_tech_keyword:
            job_data = {
                'platform': 'Discord',
                'source': message.guild.name if message.guild else 'DM',
                'title': f"Discord job post from {message.author}",
                'author': str(message.author),
                'content': content,
                'url': f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else "DM",
                'created_at': datetime.now().isoformat()
            }
            
            await self.on_job_found(job_data)

    async def start(self):
        if self.config.discord_token:
            try:
                await self.client.start(self.config.discord_token)
            except Exception as e:
                print(f"Discord connection failed: {e}")
                return False
        return True

    def stop(self):
        if self.client:
            asyncio.create_task(self.client.close())
