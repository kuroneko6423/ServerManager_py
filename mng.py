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


async def mng(msg,client,groups):
    command=msg.content.content.split('/',1)[1].split(' ')
    op=command[0]
    guild = msg.guild
    if op=="ban":
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        for x in msg.raw_mentions():
            await msg.guild.ban(client.get_user(x))
            await msg.channel.send("Baned")
    elif op=="unban":
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        for x in msg.raw_mentions():
            await msg.guild.unban(client.get_user(x))
            await msg.channel.send("Unbaned")
    elif op=="kick":
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        for x in msg.raw_mentions():
            await msg.guild.kick(client.get_user(x))
            await msg.channel.send("Kicked")
    else:
        await msg.channel.send("Unknown mng command!")