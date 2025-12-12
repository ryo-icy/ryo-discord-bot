import aiohttp
import asyncio
import datetime
import discord
from discord.ext import commands, tasks
import os

# P2P地震情報 API v2
API_URL = "https://api.p2pquake.net/v2/history"

QUAKE_ALERT_CHANNEL = int(os.getenv('QUAKE_ALERT_CHANNEL'))

class QuakeAlert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.seen_ids = set()
        self.alert_channel_id = QUAKE_ALERT_CHANNEL
        self.quake_loop.start()

    def cog_unload(self):
        self.quake_loop.cancel()

    @tasks.loop(seconds=10.0)  # 10秒ごとにAPIを確認
    async def quake_loop(self):
        # Botが準備完了するまで待機
        await self.bot.wait_until_ready()

        channel = self.bot.get_channel(self.alert_channel_id)
        if not channel:
            print(f"Error: Channel ID {self.alert_channel_id} not found.")
            return

        try:
            # APIから情報を取得 (コード551:地震, 552:津波)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_URL}?codes=551&codes=552&limit=5") as response:
                    if response.status != 200:
                        return
                    data = await response.json()

            # データは新しい順に来るので、古い順に処理するために逆順にする
            for item in reversed(data):
                event_id = item.get("id")

                # 既に処理済みのイベントはスキップ
                if event_id in self.seen_ids:
                    continue
                
                # 初回起動時は通知せず、IDだけ記録して終了（大量通知防止）
                if not self.seen_ids:
                    self.seen_ids.add(event_id)
                    continue

                # --- イベント処理 ---
                code = item.get("code")
                
                # 551: 地震情報
                if code == 551:
                    earthquake = item.get("earthquake", {})
                    max_scale = earthquake.get("maxScale", 0)

                    # 震度4以上 (P2P地震情報のスケール: 40=震度4, 45=5弱, 50=5強...)
                    if max_scale >= 40:
                        await self.send_quake_info(channel, item)
                        self.seen_ids.add(event_id)
                    else:
                        # 震度3以下でも処理済みとしてマークしないと、何度もチェックしてしまうため追加
                        self.seen_ids.add(event_id)

                # 552: 津波予報
                elif code == 552:
                    await self.send_tsunami_info(channel, item)
                    self.seen_ids.add(event_id)
            
            # メモリ節約のため、保存IDが多すぎたら古いものを削除（任意）
            if len(self.seen_ids) > 100:
                self.seen_ids = set(list(self.seen_ids)[-50:])

        except Exception as e:
            print(f"Quake Alert Error: {e}")

    async def send_quake_info(self, channel, data):
        eq = data.get("earthquake", {})
        hypocenter = eq.get("hypocenter", {})
        
        # 震度の数値を文字列に変換
        scale_map = {
            40: "震度4", 45: "震度5弱", 50: "震度5強", 
            55: "震度6弱", 60: "震度6強", 70: "震度7"
        }
        max_scale_str = scale_map.get(eq.get("maxScale"), "不明")
        
        embed = discord.Embed(title="🔴 地震情報", color=discord.Color.red())
        embed.add_field(name="最大震度", value=max_scale_str, inline=True)
        embed.add_field(name="発生時刻", value=eq.get("time"), inline=True)
        embed.add_field(name="震源地", value=hypocenter.get("name"), inline=False)
        embed.add_field(name="マグニチュード", value=f"M{hypocenter.get('magnitude')}", inline=True)
        embed.add_field(name="深さ", value=f"{hypocenter.get('depth')}km", inline=True)
        
        # 津波の有無
        tsunami_comments = {
            "None": "津波の心配なし", 
            "Unknown": "調査中", 
            "Checking": "調査中", 
            "NonEffective": "若干の海面変動あり(被害なし)", 
            "Watch": "津波注意報", 
            "Warning": "津波警報"
        }
        tsunami_status = tsunami_comments.get(eq.get("domesticTsunami"), "情報なし")
        embed.add_field(name="津波の心配", value=tsunami_status, inline=False)

        await channel.send(embed=embed)

    async def send_tsunami_info(self, channel, data):
        # 津波予報の詳細パースは複雑なため、キャンセルの場合と予報の場合で簡易表示
        cancelled = data.get("cancelled", False)
        
        title = "🌊 津波予報解除" if cancelled else "🌊 津波予報発表"
        color = discord.Color.green() if cancelled else discord.Color.blue()
        
        embed = discord.Embed(title=title, color=color)
        embed.description = "津波予報が発表または更新されました。\n沿岸部の方は情報に注意してください。"
        embed.set_footer(text=f"発表時刻: {data.get('time')}")
        
        await channel.send(embed=embed)

# main.pyでロードするためのセットアップ関数
async def setup(bot):
    await bot.add_cog(QuakeAlert(bot))