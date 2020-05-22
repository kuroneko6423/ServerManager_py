import os
import discord
import sys
import ast
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from tinydb import TinyDB, Query
from discord.ext import tasks

async def helps(msg):
  embed = discord.Embed(title="Help",description="")
  embed.add_field(name="Debug Command",value=(
    "`debug/profile Mention` メンションされた人のプロフィールを表示します.\n"
    "`debug/profile UserID` ID指定された人のプロフィールを表示します.\n"
    "`debug/info` サーバーの詳細を表示します"
    "`debug/info ServerID` コマンドを実行した人のプロフィールを表示します。"
    ),inline=False)
  embed.add_field(name="Voice Chat Command",value=(
    "`vc/create` 普遍的なボイスチャンネルを作成します"
    ),inline=False)
  embed.add_field(name="Setting Command",value=(
    "`set/creater_role` クリエイターロールを設定します。設定することにより、クリエイターしかコマンドを実行できなくなります。\n"
    "`set/vc_categories <カテゴリ名>` VCを作成するカテゴリを指定します。"
    ),inline=False)
  embed.add_field(name="Manage Command",value=(
    "`mng/ban <Mention>` Ban\n"
    "`mng/kick <Mention>` Kick.\n"
    "`mng/unban <Mention>` Unban\n"
    # "`mng/bans` Show listed bans."
    ),inline=False)
#   embed.add_field(name="System Command ( Only use cronちゃん )",value=(
#     "`sys/save`\n"
#     "`sys/load`"
#     ),inline=False)
  await msg.channel.send(embed=embed)