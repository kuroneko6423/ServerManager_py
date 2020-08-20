import discord
from discord import member


async def cmd_msg(msg, client, db, config):
    try:
        guild = msg.guild
        lang = db[guild.id]['lang']
        command = msg.content.split('/', 1)[1].split(' ')
        op = command[0]
        if op == "join":
            if command[1] not in ["on","off"]:
                msg.channel.send("msg/join [on|off]")
            else:
                if command[1] == "on":
                    db[guild.id]['setting']['send_member_join'] = "true"
                elif command[1] == "off":
                    db[guild.id]['setting']['send_member_join'] = "false"
                msg.channel.send(
                    config['msg'][lang]['msg']['join']['message']
                    .replace("%value%",command[1])
                )
        elif op=="join_message":
                db[guild.id]['setting']['send_member_join_message'] = " ".join(command[1:])
    except Exception:
        pass


async def member_event(event,member,db,client,config):
    guild = member.guild
    lang = db[guild.id]['lang']
    if db[guild.id]['setting']['send_member_'+event] is "true":
        ch = client.get_channel(db[guild.id]['setting']['send_channel'])
        try:
            ch.send(
                db[guild.id]['setting']['send_member_'+event+'_message']
                    .replace("%user%", member.mention)
                    .replace("%name%", member.name)
                    .replace("%newline%", "\n")
            )
        except discord.Forbidden:
            guild.owner.send(
                config['msg'][lang]['permission']['dm']
                    .replace('%server%', guild.name)
                    .replace('%channel%', ch.name)
            )
            guild.owner.send(
                db[guild.id]['setting']['send_member_'+event+'_message']
                    .replace("%user%", member.mention)
                    .replace("%name%", member.name)
                    .replace("%newline%", "\n")
            )
        except Exception:
            try:
                ch.send(config['msg'][lang]['error']['ch'])
            except discord.Forbidden:
                guild.owner.send(
                    config['msg'][lang]['permission']['dm']
                        .replace('%server%', guild.name)
                        .replace('%channel%', ch.name)
                )
                guild.owner.send(config['msg'][lang]['error']['ch'])
