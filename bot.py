import os

import discord
from discord.ext import commands

from dotenv import load_dotenv
import subprocess
import pandas as pd
from random import randint, seed

EXEC_FILE = 'chair_scraper.py'
RESULT_JSON = 'chair_scrapper_result.json'

DICE_UNICODE = '🎲'
ADD_ITEM_PRICE = 8_000

load_dotenv(".env")
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

items = {
    'coin': {
        'unicode': '🪙'
    },
    'bread': {
        'unicode': '🍞',
        'price': 2.
    },
    'house': {
        'unicode': '🏠',
        'price': 1_000.
    },
    'hostal': {
        'unicode': '🏩',
        'price': 3_000.
    },
    'wheat': {
        'unicode': '🌿',
        'price': 0.75
    },
    'axe': {
        'unicode': '🪓',
        'price': 50.
    },
    'horse': {
        'unicode': '🐎',
        'price': 135.
    }
}

user_possesions = {}

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

def init_user():
    result = {}
    for item in items:
        if item in ['house', 'hostal']:
            result[item] = False

        else:
            result[item] = 0

    return result


@bot.command(name='check-coins', help="Check all users coin status")
async def check_points(context):
    result = ''
    author = context.message.author
    if author == bot.user:
        return

    if not str(author.id) in user_possesions:
        user_possesions[str(author.id)] = init_user()
        result += f"{author.name} joined the game!\n\n"

    for id in user_possesions:
        user = await bot.fetch_user(int(id))
        result += f"{user.name}\t{user_possesions[id]['coin']}{items['coin']['unicode']}"
    
    await context.send(result)


@bot.command(name='items', help="Check all items prices")
async def check_items(context):
    result = ''
    author = context.message.author
    if author == bot.user:
        return

    if not str(author.id) in user_possesions:
        user_possesions[str(author.id)] = init_user()
        result += f"{author.name} joined the game!\n\n"

    for item in items:
        if item != 'coin':
            result += f"{items[item]['unicode']} -> {items[item]['price']} {items['coin']['unicode']}\n"
    
    await context.send(result)


@bot.command(name='buy', help="Buy an item")
async def buy(context, item_name):
    author = context.message.author
    if author == bot.user:
        return

    if not str(author.id) in user_possesions:
        user_possesions[str(author.id)] = init_user()
        await context.send(f"{author.name} joined the game!")

    item_name = item_name.lower()
    if item_name == 'coin':
        return

    try:
        if user_possesions[str(author.id)]['coin'] >= items[item_name]['price']:

            user_possesions[str(author.id)]['coin'] -= items[item_name]['price']

            if item_name in ['house', 'hostal']:
                user_possesions[str(author.id)][item_name] = True

            else:
                user_possesions[str(author.id)][item_name] += 1
            
            await context.send(f"Bought {item_name[0].upper() + item_name[1:]} {items[item_name]['unicode']}")

    except:
        await context.send(f"Incorrect item name \'{item_name}\'. Options are: bread, wheat, house, hostal.")


@bot.command(name='check-possesions', help="Check your item status")
async def check_possesions(context):
    author = context.message.author
    result = ''
    if author == bot.user:
        return

    if not str(author.id) in user_possesions:
        user_possesions[str(author.id)] = init_user()
        result += f"{author.name} joined the game!\n\n"

    user = await bot.fetch_user(author.id)
    result += f"{user.name}\n"

    for item in user_possesions[str(author.id)]:
        if item in ['house', 'hostal']:
            result += f"\t{item[0].upper() + item[1:]} -> {'obtained' if user_possesions[str(author.id)][item] else 'not obtained'} {items[item]['unicode']}\n"
            
        else:
            result += f"\t{item[0].upper() + item[1:]} -> {user_possesions[str(author.id)][item]} {items[item]['unicode']}\n"
        
    
    await context.send(result)


@bot.command(name='check-chairs', help="Seach n cheapest chairs from Amazon")
async def send_cheaper_chairs(context, n=5):
    subprocess.run(['scrapy', 'runspider', EXEC_FILE, '-O', RESULT_JSON])
    df = pd.read_json(RESULT_JSON)
    df = df.sort_values(by=['price'], ascending=False)
        

    for i in range(int(n)):
        row = df.iloc[i]
            
        await context.send(f"Chair: {row['name']} rated as {row['rate']} 💸 -> {row['price']}")


@bot.command(name='grind-coin', help="Get coins")
async def gain_coins(context):
    result = ''
    author = context.message.author
    if author == bot.user:
        return

    if not str(author.id) in user_possesions:
        user_possesions[str(author.id)] = init_user()
        result = f"{author.name} joined the game!\n"
    
    
    seed()
    if randint(0, 2)  == 2:
        user_possesions[str(author.id)]['coin'] += 1
        await context.send(result + f"{author.name} gained 1 coin!")
    else:
        await context.send(result + f"Bad luck!")


@bot.command(name='roll-dice', help="Roll a dice, if 7, double your coins, else loose everything")
async def roll(context):
    author = context.message.author
    if author == bot.user:
        return

    if not str(author.id) in user_possesions:
        user_possesions[str(author.id)] = init_user()
        await context.send(f"{author.name} joined the game!")

    seed()
    dice_result = randint(1,7)
    result = f"{dice_result} {DICE_UNICODE}! {author.name} "

    if dice_result == 7:
        user_possesions[str(author.id)]['coin'] += user_possesions[str(author.id)]['coin']
        await context.send(result + "doubled his/her coins!")
    
    else:
        user_possesions[str(author.id)]['coin'] = 0.
        await context.send(result + "lost all his/her coins!")


@bot.command(name='add-item', help="Add new item for 8.000 coins")
async def add_item(context, name, emoji, price):
    author = context.message.author
    if author == bot.user:
        return

    if not str(author.id) in user_possesions:
        user_possesions[str(author.id)] = init_user()
        await context.send(f"{author.name} joined the game!")

    if user_possesions[str(author.id)]['coin'] >= ADD_ITEM_PRICE:
        user_possesions[str(author.id)]['coin'] -= ADD_ITEM_PRICE

        items[name.lower()] = {
            'unicode': emoji,
            'price': float(price)
        }
        for user in user_possesions:
            user_possesions[user][name] = 0
    


bot.run(TOKEN)
