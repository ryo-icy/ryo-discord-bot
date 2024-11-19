import os
import random

import discord
from discord.ext import commands
from discord.app_commands import describe

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
tree = bot.tree

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        content_list = f.read().split('\n')
    return content_list

omikuji_list = load_config('./config/omikuji.txt')
neo_omikuji_list = load_config('./config/neo_omikuji.txt')
mention_response = load_config('./config/mention.txt')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.CustomActivity(name='**りょう**を監視中'))
    await tree.sync()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if bot.user in message.mentions:
        await message.channel.send(random.choice(mention_response))

@tree.command(name='omikuji', description='おみくじを引くことができます')
@describe(arg='[回数(1~3)]')
async def omikuji(ctx: discord.Interaction, arg: int):
    if arg >= 1 and arg <= 3:
        await ctx.response.send_message(random.choices(omikuji_list, k=arg))
    else:
        await ctx.response.send_message('引数には1～3までの整数を指定してください', ephemeral=True)

@tree.command(name='neo_omikuji', description='すごいおみくじを引くことができます')
async def neo_omikuji(ctx: discord.Interaction):
    await ctx.response.send_message(random.choice(neo_omikuji_list))

bot.run(DISCORD_TOKEN)