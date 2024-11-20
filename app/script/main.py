import os
import random

import discord
from discord.ext import commands
from discord.app_commands import describe

# Discord Botのトークンを環境変数から取得
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
tree = bot.tree

# コンフィグファイルの読み込み
def load_config(path: str) -> list[str]:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().split('\n')

omikuji_list = load_config('./config/omikuji.txt')
neo_omikuji_list = load_config('./config/neo_omikuji.txt')
mention_response = load_config('./config/mention.txt')

# おみくじメッセージを送信する処理
async def send_omikuji_message(ctx: discord.Interaction, messages: list, count: int = 1) -> None:
    await ctx.response.send_message(str(random.choices(messages, k=count)))

# BOT起動時の処理
@bot.event
async def on_ready() -> None:
    await bot.change_presence(activity=discord.CustomActivity(name='**りょう**を監視中'))
    await tree.sync()

# メッセージを受信した際の処理
@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user:
        return
    
    if bot.user in message.mentions:
        await message.channel.send(random.choice(mention_response))

# おみくじコマンド
@tree.command(name='omikuji', description='おみくじを引くことができます')
@describe(arg='[回数(1~3)]')
async def omikuji(ctx: discord.Interaction, arg: int) -> None:
    if 1 <= arg <= 3:
        await send_omikuji_message(ctx, omikuji_list, arg)
    else:
        await ctx.response.send_message('引数には1～3までの整数を指定してください', ephemeral=True)

# ネオおみくじコマンド
@tree.command(name='neo_omikuji', description='すごいおみくじを引くことができます')
async def neo_omikuji(ctx: discord.Interaction):
    await send_omikuji_message(ctx, neo_omikuji_list)

# BOTの起動
bot.run(DISCORD_TOKEN)