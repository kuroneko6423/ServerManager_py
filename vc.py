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

async def vc(msg,client,groups):
    command=msg.content.split('/',1)[1].split(' ')
    op=command[0]
    if op=="create":
        guild = msg.guild
        if 'creater_role' not in groups[guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        else:
            ch = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(groups[guild.id]['vc_categories'])].create_voice_channel("➕ 新規作成["+msg.content[10:]+"]")
            if 'vc_ch' in groups[msg.guild.id]:
                groups[msg.guild.id]['vc_ch'][ch.id] = {'kind': 'ROOT','name': msg.content[10:],'leafs': [],'root': None}
            else:
                groups[msg.guild.id]['vc_ch'] = {}
                groups[msg.guild.id]['vc_ch'][ch.id] = {'kind': 'ROOT','name': msg.content[10:],'leafs': [],'root': None}
            await msg.channel.send("Created!")
    else:
        await msg.channel.send("Unknown vc command!")
