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
    if op=="create":
        if 'creater_role' in groups[guild.id]:
            if guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
                await msg.channel.send("Creater's role is already registered.")
                return(0)
        roles = {}
        result = ""
        i = 1
        for x in guild.roles[::-1]:
            result = result+'{0}. {1}\n'.format(i,x.name)
            roles[i] = x.id
            i+=1
        embed = discord.Embed(title="Roles", description=result)
        await msg.channel.send(embed=embed)

        def check(m):
            return m.author == msg.author and m.channel == msg.channel

        try:
            m = await client.wait_for("message",timeout=10.0,check=check)
        except asyncio.TimeoutError:
            await msg.channel.send("Time outed!")
        else:
            await msg.channel.send("対象にする絵文字を入力してください。")
            try:
                m2 = await client.wait_for("message",timeout=10.0,check=check)
            except asyncio.TimeoutError:
                await msg.channel.send("Time outed!")
            else:
                await msg.channel.send("Emojiを"+str(m2)+"に登録しました。")
                msg = await msg.channel.send("このメッセージにリアクション"+str(m2)+"を付与すると、ロール"+guild.get_role(roles[int(m.content)]).name+"が付与されます。")
                await msg.add_reaction(str(m2))
                if 'reaction_msgs' not in groups[guild.id]:
                    groups[guild.id][reaction_msgs] = {}
                groups[guild.id][reaction_msgs][msg.id]=[str(m2),roles[int(m.content)]).id]