import subprocess

import discord

from main import guild_join
from util import get_announce_channel


async def cmd_admin(msg, client, db, config):
    guild = msg.guild
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    if op == "call_on_join":
        await guild_join(guild)
        await msg.channel.send("done")
        return 0
    lang = db[guild.id]['lang']
    try:
        if msg.author.id != 431707293692985344:
            try:
                await msg.channel.send(config['msg'][lang]['admin']['permission'])
            except discord.Forbidden:
                guild.owner.send(
                    config['msg'][lang]['permission']['dm']
                        .replace('%server%', guild.name)
                        .replace('%channel%', msg.channel)
                )
                guild.owner.send(config['msg'][lang]['admin']['permission'])
            return 0

        if op == "broadcast":
            for x in client.guilds:
                try:
                    get_announce_channel(guild).send(" ".join(command[1:]))
                    await msg.channel.send("Sended to `" + x.name + "` in `" + ch.name + "`")
                except discord.Forbidden:
                    await msg.channel.send("Guild:`" + x.name + "`では`" + ch.name + "`に送る権限がありません。")
        elif op == "get_db":
            await msg.author.send(file=discord.File("db.yml", filename="db.yml"))
            await msg.author.send(db)
        elif op == "get_config":
            await msg.author.send(file=discord.File("config.yml", filename="config.yml"))
        elif op == "get_logs":
            await msg.author.send(file=discord.File("logger.log", filename="logger.log"))
        elif op == "invites":
            guilds = client.guilds
            for x in guilds:
                try:
                    guild = x
                    embed = discord.Embed(title=guild.name + ":" + str(guild.id), description=guild.description)
                    embed.add_field(name="Emojis", value=guild.emojis, inline=False)
                    embed.add_field(name="Region", value=guild.region, inline=False)
                    embed.add_field(name="AFK", value="TimeOut: " + str(guild.afk_timeout) +
                                                      "\nChannel:" + str(guild.afk_channel), inline=False)
                    embed.add_field(name="Icon", value=guild.icon, inline=False)
                    embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name + "#" +
                                                        client.get_user(guild.owner_id).discriminator + ":" + str(
                        guild.owner_id), inline=False)
                    invite = await guild.invites()
                    invites = list(map(lambda x: str(x), invite))
                    embed.add_field(name="Invite", value=invites, inline=False)
                    embed.add_field(name="Created", value="at " +
                                                          guild.created_at.strftime("%Y/%m/%d"), inline=False)
                    embed.set_thumbnail(url=str(guild.banner_url))
                    await msg.channel.send(embed=embed)
                except Exception as e:
                    try:
                        await msg.channel.send("Error: " + str(e))
                    except discord.Forbidden:
                        guild.owner.send(
                            config['msg'][lang]['permission']['dm']
                                .replace('%server%', guild.name)
                                .replace('%channel%', msg.channel)
                        )
                        guild.owner.send("Error: " + str(e))
        else:
            await msg.channel.send(config['msg'][lang]['unknown']['ch'])
    except discord.Forbidden:
        try:
            await msg.channel.send(config['msg'][lang]['permission']['ch'])
        except discord.Forbidden:
            guild.owner.send(config['msg'][lang]['permission']['dm']
                             .replace('%server%', guild.name)
                             .replace('%channel%', msg.channel)
                             )
            await msg.channel.send(config['msg'][lang]['permission']['ch'])
    except:
        try:
            await msg.channel.send(config['msg'][lang]['error']['ch'])
        except discord.Forbidden:
            guild.owner.send(config['msg'][lang]['permission']['dm']
                             .replace('%server%', guild.name)
                             .replace('%channel%', msg.channel)
                             )
            guild.owner.send(config['msg'][lang]['error']['ch'])
