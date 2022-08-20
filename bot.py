import os

import discord
from discord.ext import commands

from dotenv import load_dotenv
import subprocess
import pandas as pd

EXEC_FILE = 'chair_scraper.py'
RESULT_JSON = 'chair_scrapper_result.json'

load_dotenv(".env")
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.command(name='check-chairs', help="Seach n cheapest chairs from Amazon")
async def send_cheaper_chairs(context, n=5):
    subprocess.run(['scrapy', 'runspider', EXEC_FILE, '-O', RESULT_JSON])
    df = pd.read_json(RESULT_JSON)
    df = df.sort_values(by=['price'], ascending=False)
        

    for i in range(int(n)):
        row = df.iloc[i]
            
        await context.send(f"Chair: {row['name']} rated as {row['rate']} 💸 -> {row['price']}")


bot.run(TOKEN)
