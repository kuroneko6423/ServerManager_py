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

async def debug(msg,client):
    command=msg.content.split('/',1)[1].split(' ')
    op=command[0]
    if op=="profile":
        if msg.raw_mentions!=[]:
            for user_id in msg.raw_mentions:
                user=msg.guild.get_member(user_id)
                embed = discord.Embed(title=(user.name+"#"+user.discriminator), description=str(user.id))
                embed.add_field(name="JOINED_AT",value=user.joined_at.strftime("%Y/%m/%d"),inline=False)
                embed.add_field(name="NickName",value=user.nick,inline=False)
                embed.add_field(name="Status",value=user.status,inline=False)
                embed.add_field(name="Roles",value="\n".join(map(lambda x: x.name+":"+str(x.id),user.roles)),inline=False)
                embed.add_field(name="Top Role",value=user.top_role.name+":"+str(user.top_role.id),inline=False)
                embed.add_field(name="Display Name", value=user.display_name,inline=False)
                embed.add_field(name="Activity", value=user.activity,inline=False)
                embed.set_thumbnail(url=str(user.avatar_url))
                await msg.channel.send(embed=embed)
        elif command[1:]!=[]:
            for user_id in command[1:]:
                user = msg.guild.get_member(int(user_id))
                embed = discord.Embed(title=(user.name+"#"+user.discriminator), description=str(user.id))
                embed.add_field(name="JOINED_AT",value=user.joined_at.strftime("%Y/%m/%d"),inline=False)
                embed.add_field(name="NickName",value=user.nick,inline=False)
                embed.add_field(name="Status",value=user.status,inline=False)
                embed.add_field(name="Roles",value="\n".join(map(lambda x: x.name+":"+str(x.id),user.roles)),inline=False)
                embed.add_field(name="Top Role",value=user.top_role.name+":"+str(user.top_role.id),inline=False)
                embed.add_field(name="Display Name", value=user.display_name,inline=False)
                embed.add_field(name="Activity", value=user.activity,inline=False)
                embed.set_thumbnail(url=str(user.avatar_url))
                await msg.channel.send(embed=embed)
        else:
            user = msg.author
            embed = discord.Embed(title=(user.name+"#"+user.discriminator), description=str(user.id))
            embed.add_field(name="JOINED_AT",value=user.joined_at.strftime("%Y/%m/%d"),inline=False)
            embed.add_field(name="NickName",value=user.nick,inline=False)
            embed.add_field(name="Status",value=user.status,inline=False)
            embed.add_field(name="Roles",value="\n".join(map(lambda x: x.name+":"+str(x.id),user.roles)),inline=False)
            embed.add_field(name="Top Role",value=user.top_role.name+":"+str(user.top_role.id),inline=False)
            embed.add_field(name="Display Name", value=user.display_name,inline=False)
            embed.add_field(name="Activity", value=user.activity,inline=False)
            embed.set_thumbnail(url=str(user.avatar_url))
            await msg.channel.send(embed=embed)
    elif op=="info":
        if command[1:]!=[]:
            for guild_id in command[1:]:
                guild = client.get_guild(int(guild_id))
                embed = discord.Embed(title=guild.name+":"+str(guild.id), description=guild.description)
                embed.add_field(name="Emojis", value=guild.emojis,inline=False)
                embed.add_field(name="Region", value=guild.region,inline=False)
                embed.add_field(name="AFK", value="TimeOut: "+str(guild.afk_timeout)+"\nChannel:"+str(guild.afk_channel),inline=False)
                embed.add_field(name="Icon", value=guild.icon,inline=False)
                embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name+"#"+client.get_user(guild.owner_id).discriminator+":"+str(guild.owner_id),inline=False)
                embed.add_field(name="Created",value="at "+guild.created_at.strftime("%Y/%m/%d"),inline=False)
                embed.set_thumbnail(url=str(guild.banner_url))
                await msg.channel.send(embed=embed)
        else:
            guild = msg.guild
            embed = discord.Embed(title=guild.name+":"+str(guild.id), description=guild.description)
            embed.add_field(name="Emojis", value=guild.emojis,inline=False)
            embed.add_field(name="Region", value=guild.region,inline=False)
            embed.add_field(name="AFK", value="TimeOut: "+str(guild.afk_timeout)+"\nChannel:"+str(guild.afk_channel),inline=False)
            embed.add_field(name="Icon", value=guild.icon,inline=False)
            embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name+"#"+client.get_user(guild.owner_id).discriminator+":"+str(guild.owner_id),inline=False)
            embed.add_field(name="Created",value="at "+guild.created_at.strftime("%Y/%m/%d"),inline=False)
            embed.set_thumbnail(url=str(guild.banner_url))
            await msg.channel.send(embed=embed)
    else:
        await msg.channel.send("Unkown debug command!")