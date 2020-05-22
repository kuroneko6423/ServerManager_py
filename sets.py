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


async def sets(msg,client,groups):
    command=msg.content.split('/',1)[1].split(' ')
    op=command[0]
    if op=="creater_role":
        guild = msg.guild
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
            if int(m.content) in roles:
                groups[guild.id]['creater_role'] = roles[int(m.content)]
                await msg.channel.send(guild.get_role(roles[int(m.content)]).name+" has been registered as the role of creator.")
            else:
                await msg.channel.send("Unknown reaction!")
    elif op=="vc_categories":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        else:
            categories = command[1]
            if categories not in guild.categories:
                await msg.channel.send("Unkown categorie "+categories)
                return(0)
            groups[msg.guild.id]['vc_categories'] = msg.content[18:]
            await msg.channel.send("I set "+msg.content[18:]+" to the voice chat category.")
    else:
        await msg.channel.send("Unkown set command!")
