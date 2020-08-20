import os
import discord
import asyncio
import yaml
from dotenv import load_dotenv
from discord.ext import tasks
import logger
if __name__ == "__main__":
    from commands.admin import cmd_admin
from commands.help import cmd_help
from commands.msg import cmd_msg
from commands.msg import member_event
from util import get_channel_from_name, get_announce_channel, reload_activity

db_file = open("db.yml", "r+")
db = yaml.load(db_file)

config_file = open("config.yml", "r+")
config = yaml.load(config_file)

logging = logger.Logger('main')

load_dotenv()
TOKEN = os.environ["TOKEN"]
client = discord.Client()

# ads = config['ads']


@client.event
async def on_message(msg):
    global db
    guild = msg.guild
    if msg.author.bot:
        return
    op = msg.content.split('/', 1)[0]
    if msg.content == "/help":
        await cmd_help(msg, client, db, config)
    elif op == "admin":
        await cmd_admin(msg, client, db, config)
    elif op == "msg":
        await cmd_msg(msg, client, db, config)




@client.event
async def on_member_join(member):
    await member_event("join",member,db,client,config)
    await reload_activity(client, logging)


@client.event
async def on_guild_remove(guild):
    await reload_activity(client, logging)


@client.event
async def on_member_remove(member):
    await member_event("leave",member,db,client,config)
    await reload_activity(client, logging)

@tasks.loop(seconds=10)
async def db_save():
    global db
    global db_file
    db_file.write(yaml.dump(db, default_flow_style=False))
    logging.info("DB saved")


@client.event
async def on_ready():
    global db
    logging.info("Bot is ready!")
    await reload_activity(client,logging)


@client.event
async def on_connect():
    global db
    logging.info("Bot has logged in!")
    db_save.start()


@client.event
async def on_disconnect():
    global db
    logging.info("Bot has been logged out!")


@client.event
async def on_guild_join(guild):
    try:
        await reload_activity(client, logging)
        await guild_join(guild)
    except:
        pass

async def guild_join(guild):
    try:
        global db
        global config
        db[guild.id] = {}
        db[guild.id]['setting']['send_member_join'] = "false"
        db[guild.id]['setting']['send_member_leave'] = "false"
        db[guild.id]['setting']['send_member_join_message'] = config['msg'][db[guild.id]['lang']]['on_join_message']['default']
        db[guild.id]['setting']['send_channel'] = guild.system_channel.id
        db[guild.id]['setting']['send_member_leave_message'] = config['msg'][db[guild.id]['lang']]['on_leave_message']['default']
        if db.region == discord.VoiceRegion.japan:
            db[guild.id]['lang'] = "jp"
        else:
            db[guild.id]['lang'] = "en"

        logging.info("joined guild: guild_{0}({1})".format(guild.name, guild.id))
        embed = discord.Embed(
            title=config['msg'][db[guild.id]['lang']]['firstjoin']['title'],
            description=config['msg'][db[guild.id]['lang']]['firstjoin']['description'],
            color=discord.Colour.red()
        )

        try:
            get_announce_channel(guild).send(embed=embed)
        except discord.Forbidden:
            guild.owner.send(
                config['msg'][db[guild.id]['lang']]['permission']['dm']
                    .replace('%server%', guild.name)
                    .replace('%channel%', get_announce_channel(guild).name)
            )
            guild.owner.send(embed=embed)
    except:
        guild.owner.send(
            config['msg'][db[guild.id]['lang']]['error']['dm']
            .replace('%server%', guild.name)
            .replace('%channel%', get_announce_channel(guild).name)
        )

if __name__ == "__main__":
    client.run(TOKEN)

#
# @client.event
# async def on_voice_state_update(member, before, after):
#     try:
#         global db
#         if before.channel == None:
#             guild = after.channel.guild
#         else:
#             guild = before.channel.guild
#         await guild.system_channel.send('{0}が{1}から{2}へ移動しました。'.format(member, before.channel, after.channel))
#         logging.info('{0} moved from {1} to {2}'.format(member, before.channel, after.channel))
#         if before.channel != None:
#             if before.channel.id in groups[guild.id]['vc_ch']:
#                 if groups[guild.id]['vc_ch'][before.channel.id]['kind'] == 'LEAF':
#                     if before.channel.members == []:
#                         await guild.system_channel.send('{0}を、人数が{0}人になったため、削除します。'.format(before.channel.name))
#                         v = groups[guild.id]['vc_ch'].pop(before.channel.id)
#                         groups[guild.id]['vc_ch'][v['root']]['leafs'].remove(before.channel.id)
#                         await before.channel.delete()
#                         await client.get_channel(v['text']).delete()
#                     else:
#                         text_ch = client.get_channel(groups[guild.id]['vc_ch'][before.channel.id]['text'])
#                         await text_ch.set_permissions(member, read_messages=False, send_messages=False)
#         if after.channel != None:
#             if after.channel.id in groups[guild.id]['vc_ch']:
#                 if groups[guild.id]['vc_ch'][after.channel.id]['kind'] == 'ROOT':
#                     ch = await guild.categories[list(map(lambda x: x.name, after.channel.guild.categories)).index(
#                         groups[guild.id]['vc_categories'])].create_voice_channel(
#                         'No.{0} [{1}]'.format(len(groups[guild.id]['vc_ch'][after.channel.id]['leafs']) + 1,
#                                               groups[guild.id]['vc_ch'][after.channel.id]['name']))
#                     ch_text = await guild.categories[list(map(lambda x: x.name, after.channel.guild.categories)).index(
#                         groups[guild.id]['vc_categories'])].create_text_channel(
#                         '{1}_{0}'.format(len(groups[guild.id]['vc_ch'][after.channel.id]['leafs']) + 1,
#                                          groups[guild.id]['vc_ch'][after.channel.id]['name']))
#                     await ch_text.set_permissions(guild.default_role, read_messages=False, send_messages=False)
#                     groups[guild.id]['vc_ch'][ch.id] = {'kind': 'LEAF',
#                                                         'name': groups[guild.id]['vc_ch'][after.channel.id]['name'],
#                                                         'leafs': None, 'root': after.channel.id, 'text': ch_text.id}
#                     groups[guild.id]['vc_ch'][after.channel.id]['leafs'].append(ch.id)
#                     await member.move_to(ch)
#                 elif groups[guild.id]['vc_ch'][after.channel.id]['kind'] == 'LEAF':
#                     text_ch = client.get_channel(groups[guild.id]['vc_ch'][after.channel.id]['text'])
#                     await text_ch.set_permissions(member, read_messages=True, send_messages=True)
#     except:
#         logging.info('Guild: {0} VOICE_STATE_UPDATE ERROR'.format(guild.name))
#         print('Guild: {0} VOICE_STATE_UPDATE ERROR'.format(guild.name))
#
#
# # @tasks.loop(minutes=60)
# # async def ad():
# #     global db
# #     global ads
# #     ad = random.choice(ads)
# #     for x in client.guilds:
# #         try:
# #             embed = discord.Embed(title="[INFO]" + ad[0], description=ad[1], color=discord.Colour.red())
# #             await x.system_channel.send(embed=embed)
# #             print("Sended to " + str(x.name))
# #         except discord.Forbidden:
# #             logging.info('PERMISSION ERROR: AD guild_{0}({1})'.format(x.name, x.id))
#
#
# @client.event
# async def on_reaction_add(reaction, user):
#     global groups
#     guild = reaction.message.guild
#     if 'reaction_msgs' not in groups[guild.id]:
#         groups[guild.id]['reaction_msgs'] = {}
#     if str(reaction.message.id) in groups[guild.id]['reaction_msgs'].keys():
#         if str(reaction.emoji) == groups[guild.id]['reaction_msgs'][str(reaction.message.id)][0]:
#             await user.add_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][str(reaction.message.id)][1])))
#
#
# @client.event
# async def on_reaction_remove(reaction, user):
#     global groups
#     guild = reaction.message.guild
#     if str(reaction.message.id) in groups[guild.id]['reaction_msgs'].keys():
#         if str(reaction.emoji) == groups[guild.id]['reaction_msgs'][str(reaction.message.id)][0]:
#             await user.remove_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][str(reaction.message.id)][1])))
#
#
# async def request(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     guild = msg.guild
#     if op == "create":
#         guild = msg.guild
#         ch = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(
#             groups[guild.id]['req_categories'])].create_text_channel("Request【" + msg.content[11:] + "】")
#         ch2 = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(
#             groups[guild.id]['req_ad_categories'])].create_text_channel("Request Admin【" + msg.content[11:] + "】")
#         await msg.channel.send("作成しました。")
#     elif op == "close":
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         await msg.channel.delete()
#     else:
#         await msg.channel.send("Unknown req command!")
#
#
# async def role(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     guild = msg.guild
#     if op == "create":
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         roles = {}
#         result = ""
#         i = 1
#         for x in guild.roles[::-1]:
#             result = result + '{0}. {1}\n'.format(i, x.name)
#             roles[i] = x.id
#             i += 1
#         embed = discord.Embed(title="Roles", description=result)
#         await msg.channel.send(embed=embed)
#
#         def check(m):
#             return m.author == msg.author and m.channel == msg.channel
#
#         try:
#             m = await client.wait_for("message", timeout=10.0, check=check)
#         except asyncio.TimeoutError:
#             await msg.channel.send("Time outed!")
#         else:
#             await msg.channel.send("対象にする絵文字を入力してください。")
#             try:
#                 m2 = await client.wait_for("message", timeout=10.0, check=check)
#             except asyncio.TimeoutError:
#                 await msg.channel.send("Time outed!")
#             else:
#                 await msg.channel.send("Emojiを" + m2.content + "に登録しました。")
#                 msg = await msg.channel.send("このメッセージにリアクション" + m2.content + "を付与すると、ロール" + guild.get_role(
#                     roles[int(m.content)]).name + "が付与されます。")
#                 await msg.add_reaction(m2.content)
#                 if 'reaction_msgs' not in groups[guild.id]:
#                     groups[guild.id]["reaction_msgs"] = {}
#                 groups[guild.id]["reaction_msgs"][str(msg.id)] = [m2.content, roles[int(m.content)]]
#     else:
#         await msg.channel.send("Unkown role command!")
#
#
#
#
# async def debug(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     if op == "profile":
#         if msg.raw_mentions != []:
#             for user_id in msg.raw_mentions:
#                 user = msg.guild.get_member(user_id)
#                 embed = discord.Embed(
#                     title=(user.name + "#" + user.discriminator), description=str(user.id))
#                 embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
#                     "%Y/%m/%d"), inline=False)
#                 embed.add_field(name="NickName", value=user.nick, inline=False)
#                 embed.add_field(name="Status", value=user.status, inline=False)
#                 embed.add_field(name="Roles", value="\n".join(
#                     map(lambda x: x.name + ":" + str(x.id), user.roles)), inline=False)
#                 embed.add_field(name="Top Role", value=user.top_role.name +
#                                                        ":" + str(user.top_role.id), inline=False)
#                 embed.add_field(name="Display Name",
#                                 value=user.display_name, inline=False)
#                 embed.add_field(name="Activity",
#                                 value=user.activity, inline=False)
#                 embed.set_thumbnail(url=str(user.avatar_url))
#                 await msg.channel.send(embed=embed)
#         elif command[1:] != []:
#             for user_id in command[1:]:
#                 user = msg.guild.get_member(int(user_id))
#                 embed = discord.Embed(
#                     title=(user.name + "#" + user.discriminator), description=str(user.id))
#                 embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
#                     "%Y/%m/%d"), inline=False)
#                 embed.add_field(name="NickName", value=user.nick, inline=False)
#                 embed.add_field(name="Status", value=user.status, inline=False)
#                 embed.add_field(name="Roles", value="\n".join(
#                     map(lambda x: x.name + ":" + str(x.id), user.roles)), inline=False)
#                 embed.add_field(name="Top Role", value=user.top_role.name +
#                                                        ":" + str(user.top_role.id), inline=False)
#                 embed.add_field(name="Display Name",
#                                 value=user.display_name, inline=False)
#                 embed.add_field(name="Activity",
#                                 value=user.activity, inline=False)
#                 embed.set_thumbnail(url=str(user.avatar_url))
#                 await msg.channel.send(embed=embed)
#         else:
#             user = msg.author
#             embed = discord.Embed(
#                 title=(user.name + "#" + user.discriminator), description=str(user.id))
#             embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
#                 "%Y/%m/%d"), inline=False)
#             embed.add_field(name="NickName", value=user.nick, inline=False)
#             embed.add_field(name="Status", value=user.status, inline=False)
#             embed.add_field(name="Roles", value="\n".join(
#                 map(lambda x: x.name + ":" + str(x.id), user.roles)), inline=False)
#             embed.add_field(name="Top Role", value=user.top_role.name +
#                                                    ":" + str(user.top_role.id), inline=False)
#             embed.add_field(name="Display Name",
#                             value=user.display_name, inline=False)
#             embed.add_field(name="Activity", value=user.activity, inline=False)
#             embed.set_thumbnail(url=str(user.avatar_url))
#             await msg.channel.send(embed=embed)
#     elif op == "info":
#         if command[1:] != []:
#             for guild_id in command[1:]:
#                 guild = client.get_guild(int(guild_id))
#                 embed = discord.Embed(
#                     title=guild.name + ":" + str(guild.id), description=guild.description)
#                 embed.add_field(
#                     name="Emojis", value=guild.emojis, inline=False)
#                 embed.add_field(
#                     name="Region", value=guild.region, inline=False)
#                 embed.add_field(name="AFK", value="TimeOut: " + str(guild.afk_timeout) +
#                                                   "\nChannel:" + str(guild.afk_channel), inline=False)
#                 embed.add_field(name="Icon", value=guild.icon, inline=False)
#                 embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name + "#" +
#                                                     client.get_user(guild.owner_id).discriminator + ":" + str(
#                     guild.owner_id), inline=False)
#                 embed.add_field(name="Created", value="at " +
#                                                       guild.created_at.strftime("%Y/%m/%d"), inline=False)
#                 embed.set_thumbnail(url=str(guild.banner_url))
#                 await msg.channel.send(embed=embed)
#         else:
#             guild = msg.guild
#             embed = discord.Embed(title=guild.name + ":" + str(guild.id), description=guild.description)
#             embed.add_field(name="Emojis", value=guild.emojis, inline=False)
#             embed.add_field(name="Region", value=guild.region, inline=False)
#             embed.add_field(name="AFK", value="TimeOut: " + str(guild.afk_timeout) +
#                                               "\nChannel:" + str(guild.afk_channel), inline=False)
#             embed.add_field(name="Icon", value=guild.icon, inline=False)
#             embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name + "#" +
#                                                 client.get_user(guild.owner_id).discriminator + ":" + str(
#                 guild.owner_id), inline=False)
#             embed.add_field(name="Created", value="at " +
#                                                   guild.created_at.strftime("%Y/%m/%d"), inline=False)
#             embed.set_thumbnail(url=str(guild.banner_url))
#             await msg.channel.send(embed=embed)
#     else:
#         await msg.channel.send("Unkown debug command!")
#
#
# async def sets(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     if op == "creater_role":
#         guild = msg.guild
#         if 'creater_role' in groups[guild.id]:
#             if guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#                 await msg.channel.send("クリエイターロールは既に設定されています。")
#                 return (0)
#         roles = {}
#         result = ""
#         i = 1
#         for x in guild.roles[::-1]:
#             result = result + '{0}. {1}\n'.format(i, x.name)
#             roles[i] = x.id
#             i += 1
#         embed = discord.Embed(title="Roles", description=result)
#         await msg.channel.send(embed=embed)
#
#         def check(m):
#             return m.author == msg.author and m.channel == msg.channel
#
#         try:
#             m = await client.wait_for("message", timeout=10.0, check=check)
#         except asyncio.TimeoutError:
#             await msg.channel.send("Time outed!")
#         else:
#             if int(m.content) in roles:
#                 groups[guild.id]['creater_role'] = roles[int(m.content)]
#                 await msg.channel.send(guild.get_role(roles[int(m.content)]).name + "をクリエイターロールに設定しました。")
#             else:
#                 await msg.channel.send("誤ったリアクションです！")
#     elif op == "vc_categories":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             categories = command[1]
#             if categories not in list(map(lambda x: x.name, guild.categories)):
#                 await msg.channel.send("カテゴリ" + categories + "は存在しません。")
#                 return (0)
#             groups[msg.guild.id]['vc_categories'] = msg.content[18:]
#             await msg.channel.send(msg.content[18:] + "をVCカテゴリに設定しました。")
#     elif op == "req_categories":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             categories = command[1]
#             if categories not in list(map(lambda x: x.name, guild.categories)):
#                 await msg.channel.send("カテゴリ" + categories + "は存在しません。")
#                 return (0)
#             groups[msg.guild.id]['req_categories'] = msg.content[19:]
#             await msg.channel.send(msg.content[19:] + "をrequestカテゴリに設定しました。")
#     elif op == "req_ad_categories":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             categories = command[1]
#             if categories not in list(map(lambda x: x.name, guild.categories)):
#                 await msg.channel.send("カテゴリ" + categories + "は存在しません。")
#                 return (0)
#             groups[msg.guild.id]['req_ad_categories'] = msg.content[22:]
#             await msg.channel.send(msg.content[22:] + "をリクエスト(admin)カテゴリに設定しました。")
#     elif op == "thread_name":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             if 'thread' not in groups[guild.id]:
#                 groups[guild.id]['thread'] = {'threads': {}}
#             name = command[1]
#             groups[guild.id]['thread']['thread_name'] = name
#             await msg.channel.send(name + "をスレッドネームに設定しました。")
#     elif op == "thread_categories":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             if 'thread' not in groups[guild.id]:
#                 groups[guild.id]['thread'] = {'threads': {}}
#             categories = command[1]
#             if categories not in list(map(lambda x: x.name, guild.categories)):
#                 await msg.channel.send("カテゴリ" + categories + "は存在しません。")
#                 return (0)
#             groups[msg.guild.id]['thread']['thread_categories'] = msg.content[22:]
#             await msg.channel.send(msg.content[22:] + "をスレッドカテゴリに設定しました。")
#     else:
#         await msg.channel.send("存在しないsetコマンドです。")
#
#
# async def vc(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     if op == "create":
#         guild = msg.guild
#         if 'creater_role' not in groups[guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         elif 'vc_categories' not in groups[guild.id]:
#             await msg.channel.send("先にVCカテゴリを設定してください。")
#             return (0)
#         else:
#             ch = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(
#                 groups[guild.id]['vc_categories'])].create_voice_channel("➕ 新規作成[" + msg.content[10:] + "]")
#             if 'vc_ch' in groups[msg.guild.id]:
#                 groups[msg.guild.id]['vc_ch'][ch.id] = {
#                     'kind': 'ROOT', 'name': msg.content[10:], 'leafs': [], 'root': None}
#             else:
#                 groups[msg.guild.id]['vc_ch'] = {}
#                 groups[msg.guild.id]['vc_ch'][ch.id] = {
#                     'kind': 'ROOT', 'name': msg.content[10:], 'leafs': [], 'root': None}
#             await msg.channel.send("作成しました！")
#     else:
#         await msg.channel.send("存在しないvcコマンドです。")
#
#
# async def thread(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     if op == "create":
#         guild = msg.guild
#         if 'thread' not in groups[guild.id]:
#             groups[guild.id]['thread'] = {'threads': {}}
#         if 'thread_categories' not in groups[guild.id]['thread']:
#             await msg.channel.send("先にスレッドカテゴリを設定してください。")
#             return (0)
#         elif 'thread_name' not in groups[guild.id]['thread']:
#             await msg.channel.send("先にスレッドネームを設定してください。")
#             return (0)
#         else:
#             if 'threads' not in groups[guild.id]['thread']:
#                 groups[guild.id]['thread']['threads'] = {}
#             categories = guild.categories[
#                 list(map(lambda x: x.name, guild.categories)).index(groups[guild.id]['thread']['thread_categories'])]
#             num = len(groups[guild.id]['thread']['threads'].keys())
#             ch = await categories.create_text_channel(
#                 str(num) + ". 【" + groups[guild.id]['thread']['thread_name'] + "】")
#             await ch.set_permissions(msg.author, read_messages=True, send_messages=True)
#             groups[guild.id]['thread']['threads'][ch.id] = msg.author.id
#             await msg.channel.send("作成しました！")
#     elif op == "close":
#         guild = msg.guild
#         if msg.channel.id not in groups[guild.id]['thread']['threads'].keys():
#             await msg.channel.send("スレッドのみを削除することができます。")
#             return (0)
#         elif msg.author.id == groups[guild.id]['thread']['threads'][msg.channel.id]:
#             await guild.system_channel.send(msg.channel.name + "を削除します。")
#             await msg.channel.delete()
#         elif guild.get_role(groups[guild.id]['creater_role']) in msg.author.roles:
#             await guild.system_channel.send(msg.channel.name + "を削除します。")
#             await msg.channel.delete()
#         else:
#             await guild.system_channel.send("このコマンドは、スレッドの作成者もしくはクリエイターのみが実行できるコマンドです。")
#     else:
#         await msg.channel.send("存在しないvcコマンドです。")
#
#
# client.run(TOKEN)
#
# """ MEMO
#
# {
#     'group_id': ID,
#     'group_name': NAME,
#     'vc': {
#         'CH_ID': {
#         'kind': 'ROOT_OR_LEAF',
#         'name': 'NAME',
#         'leafs': [LEAFS]|NONE,
#         'root': 'ROOT_ID'|NONE,
#         'text': 'TEXT_CHANNEL_ID'
#       },
#     },
#     'sets': {
#         'XXXXX': 'XXXXX',
#     }
# }
#
#
# {
#   "GROUP_ID": {
#     'vc_ch': {
#       'CH_ID': {
#         'kind': 'ROOT_OR_LEAF',
#         'name': 'NAME',
#         'leafs': [LEAFS]|NONE,
#         'root': 'ROOT_ID'|NONE,
#         'text': 'TEXT_CHANNEL_ID'
#       }
#     },
#     'reaction_msgs': {
#         'msg_id': ['emoji','role_id']
#     },
#     'thread': {
#         'thread_name': '依頼',
#         'thread_categories': 'カテゴリ',
#         'thread_role': ROLE_ID,
#         'threads': {
#             'channel_ID': 'author'
#         }
#     }
#   }
# }
##
# @client.event
# async def on_voice_state_update(member, before, after):
#     try:
#         global db
#         if before.channel == None:
#             guild = after.channel.guild
#         else:
#             guild = before.channel.guild
#         await guild.system_channel.send('{0}が{1}から{2}へ移動しました。'.format(member, before.channel, after.channel))
#         logging.info('{0} moved from {1} to {2}'.format(member, before.channel, after.channel))
#         if before.channel != None:
#             if before.channel.id in groups[guild.id]['vc_ch']:
#                 if groups[guild.id]['vc_ch'][before.channel.id]['kind'] == 'LEAF':
#                     if before.channel.members == []:
#                         await guild.system_channel.send('{0}を、人数が{0}人になったため、削除します。'.format(before.channel.name))
#                         v = groups[guild.id]['vc_ch'].pop(before.channel.id)
#                         groups[guild.id]['vc_ch'][v['root']]['leafs'].remove(before.channel.id)
#                         await before.channel.delete()
#                         await client.get_channel(v['text']).delete()
#                     else:
#                         text_ch = client.get_channel(groups[guild.id]['vc_ch'][before.channel.id]['text'])
#                         await text_ch.set_permissions(member, read_messages=False, send_messages=False)
#         if after.channel != None:
#             if after.channel.id in groups[guild.id]['vc_ch']:
#                 if groups[guild.id]['vc_ch'][after.channel.id]['kind'] == 'ROOT':
#                     ch = await guild.categories[list(map(lambda x: x.name, after.channel.guild.categories)).index(
#                         groups[guild.id]['vc_categories'])].create_voice_channel(
#                         'No.{0} [{1}]'.format(len(groups[guild.id]['vc_ch'][after.channel.id]['leafs']) + 1,
#                                               groups[guild.id]['vc_ch'][after.channel.id]['name']))
#                     ch_text = await guild.categories[list(map(lambda x: x.name, after.channel.guild.categories)).index(
#                         groups[guild.id]['vc_categories'])].create_text_channel(
#                         '{1}_{0}'.format(len(groups[guild.id]['vc_ch'][after.channel.id]['leafs']) + 1,
#                                          groups[guild.id]['vc_ch'][after.channel.id]['name']))
#                     await ch_text.set_permissions(guild.default_role, read_messages=False, send_messages=False)
#                     groups[guild.id]['vc_ch'][ch.id] = {'kind': 'LEAF',
#                                                         'name': groups[guild.id]['vc_ch'][after.channel.id]['name'],
#                                                         'leafs': None, 'root': after.channel.id, 'text': ch_text.id}
#                     groups[guild.id]['vc_ch'][after.channel.id]['leafs'].append(ch.id)
#                     await member.move_to(ch)
#                 elif groups[guild.id]['vc_ch'][after.channel.id]['kind'] == 'LEAF':
#                     text_ch = client.get_channel(groups[guild.id]['vc_ch'][after.channel.id]['text'])
#                     await text_ch.set_permissions(member, read_messages=True, send_messages=True)
#     except:
#         logging.info('Guild: {0} VOICE_STATE_UPDATE ERROR'.format(guild.name))
#         print('Guild: {0} VOICE_STATE_UPDATE ERROR'.format(guild.name))
#
#
# # @tasks.loop(minutes=60)
# # async def ad():
# #     global db
# #     global ads
# #     ad = random.choice(ads)
# #     for x in client.guilds:
# #         try:
# #             embed = discord.Embed(title="[INFO]" + ad[0], description=ad[1], color=discord.Colour.red())
# #             await x.system_channel.send(embed=embed)
# #             print("Sended to " + str(x.name))
# #         except discord.Forbidden:
# #             logging.info('PERMISSION ERROR: AD guild_{0}({1})'.format(x.name, x.id))
#
#
# @client.event
# async def on_reaction_add(reaction, user):
#     global groups
#     guild = reaction.message.guild
#     if 'reaction_msgs' not in groups[guild.id]:
#         groups[guild.id]['reaction_msgs'] = {}
#     if str(reaction.message.id) in groups[guild.id]['reaction_msgs'].keys():
#         if str(reaction.emoji) == groups[guild.id]['reaction_msgs'][str(reaction.message.id)][0]:
#             await user.add_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][str(reaction.message.id)][1])))
#
#
# @client.event
# async def on_reaction_remove(reaction, user):
#     global groups
#     guild = reaction.message.guild
#     if str(reaction.message.id) in groups[guild.id]['reaction_msgs'].keys():
#         if str(reaction.emoji) == groups[guild.id]['reaction_msgs'][str(reaction.message.id)][0]:
#             await user.remove_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][str(reaction.message.id)][1])))
#
#
# async def request(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     guild = msg.guild
#     if op == "create":
#         guild = msg.guild
#         ch = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(
#             groups[guild.id]['req_categories'])].create_text_channel("Request【" + msg.content[11:] + "】")
#         ch2 = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(
#             groups[guild.id]['req_ad_categories'])].create_text_channel("Request Admin【" + msg.content[11:] + "】")
#         await msg.channel.send("作成しました。")
#     elif op == "close":
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         await msg.channel.delete()
#     else:
#         await msg.channel.send("Unknown req command!")
#
#
# async def role(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     guild = msg.guild
#     if op == "create":
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         roles = {}
#         result = ""
#         i = 1
#         for x in guild.roles[::-1]:
#             result = result + '{0}. {1}\n'.format(i, x.name)
#             roles[i] = x.id
#             i += 1
#         embed = discord.Embed(title="Roles", description=result)
#         await msg.channel.send(embed=embed)
#
#         def check(m):
#             return m.author == msg.author and m.channel == msg.channel
#
#         try:
#             m = await client.wait_for("message", timeout=10.0, check=check)
#         except asyncio.TimeoutError:
#             await msg.channel.send("Time outed!")
#         else:
#             await msg.channel.send("対象にする絵文字を入力してください。")
#             try:
#                 m2 = await client.wait_for("message", timeout=10.0, check=check)
#             except asyncio.TimeoutError:
#                 await msg.channel.send("Time outed!")
#             else:
#                 await msg.channel.send("Emojiを" + m2.content + "に登録しました。")
#                 msg = await msg.channel.send("このメッセージにリアクション" + m2.content + "を付与すると、ロール" + guild.get_role(
#                     roles[int(m.content)]).name + "が付与されます。")
#                 await msg.add_reaction(m2.content)
#                 if 'reaction_msgs' not in groups[guild.id]:
#                     groups[guild.id]["reaction_msgs"] = {}
#                 groups[guild.id]["reaction_msgs"][str(msg.id)] = [m2.content, roles[int(m.content)]]
#     else:
#         await msg.channel.send("Unkown role command!")
#
#
#
#
# async def debug(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     if op == "profile":
#         if msg.raw_mentions != []:
#             for user_id in msg.raw_mentions:
#                 user = msg.guild.get_member(user_id)
#                 embed = discord.Embed(
#                     title=(user.name + "#" + user.discriminator), description=str(user.id))
#                 embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
#                     "%Y/%m/%d"), inline=False)
#                 embed.add_field(name="NickName", value=user.nick, inline=False)
#                 embed.add_field(name="Status", value=user.status, inline=False)
#                 embed.add_field(name="Roles", value="\n".join(
#                     map(lambda x: x.name + ":" + str(x.id), user.roles)), inline=False)
#                 embed.add_field(name="Top Role", value=user.top_role.name +
#                                                        ":" + str(user.top_role.id), inline=False)
#                 embed.add_field(name="Display Name",
#                                 value=user.display_name, inline=False)
#                 embed.add_field(name="Activity",
#                                 value=user.activity, inline=False)
#                 embed.set_thumbnail(url=str(user.avatar_url))
#                 await msg.channel.send(embed=embed)
#         elif command[1:] != []:
#             for user_id in command[1:]:
#                 user = msg.guild.get_member(int(user_id))
#                 embed = discord.Embed(
#                     title=(user.name + "#" + user.discriminator), description=str(user.id))
#                 embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
#                     "%Y/%m/%d"), inline=False)
#                 embed.add_field(name="NickName", value=user.nick, inline=False)
#                 embed.add_field(name="Status", value=user.status, inline=False)
#                 embed.add_field(name="Roles", value="\n".join(
#                     map(lambda x: x.name + ":" + str(x.id), user.roles)), inline=False)
#                 embed.add_field(name="Top Role", value=user.top_role.name +
#                                                        ":" + str(user.top_role.id), inline=False)
#                 embed.add_field(name="Display Name",
#                                 value=user.display_name, inline=False)
#                 embed.add_field(name="Activity",
#                                 value=user.activity, inline=False)
#                 embed.set_thumbnail(url=str(user.avatar_url))
#                 await msg.channel.send(embed=embed)
#         else:
#             user = msg.author
#             embed = discord.Embed(
#                 title=(user.name + "#" + user.discriminator), description=str(user.id))
#             embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
#                 "%Y/%m/%d"), inline=False)
#             embed.add_field(name="NickName", value=user.nick, inline=False)
#             embed.add_field(name="Status", value=user.status, inline=False)
#             embed.add_field(name="Roles", value="\n".join(
#                 map(lambda x: x.name + ":" + str(x.id), user.roles)), inline=False)
#             embed.add_field(name="Top Role", value=user.top_role.name +
#                                                    ":" + str(user.top_role.id), inline=False)
#             embed.add_field(name="Display Name",
#                             value=user.display_name, inline=False)
#             embed.add_field(name="Activity", value=user.activity, inline=False)
#             embed.set_thumbnail(url=str(user.avatar_url))
#             await msg.channel.send(embed=embed)
#     elif op == "info":
#         if command[1:] != []:
#             for guild_id in command[1:]:
#                 guild = client.get_guild(int(guild_id))
#                 embed = discord.Embed(
#                     title=guild.name + ":" + str(guild.id), description=guild.description)
#                 embed.add_field(
#                     name="Emojis", value=guild.emojis, inline=False)
#                 embed.add_field(
#                     name="Region", value=guild.region, inline=False)
#                 embed.add_field(name="AFK", value="TimeOut: " + str(guild.afk_timeout) +
#                                                   "\nChannel:" + str(guild.afk_channel), inline=False)
#                 embed.add_field(name="Icon", value=guild.icon, inline=False)
#                 embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name + "#" +
#                                                     client.get_user(guild.owner_id).discriminator + ":" + str(
#                     guild.owner_id), inline=False)
#                 embed.add_field(name="Created", value="at " +
#                                                       guild.created_at.strftime("%Y/%m/%d"), inline=False)
#                 embed.set_thumbnail(url=str(guild.banner_url))
#                 await msg.channel.send(embed=embed)
#         else:
#             guild = msg.guild
#             embed = discord.Embed(title=guild.name + ":" + str(guild.id), description=guild.description)
#             embed.add_field(name="Emojis", value=guild.emojis, inline=False)
#             embed.add_field(name="Region", value=guild.region, inline=False)
#             embed.add_field(name="AFK", value="TimeOut: " + str(guild.afk_timeout) +
#                                               "\nChannel:" + str(guild.afk_channel), inline=False)
#             embed.add_field(name="Icon", value=guild.icon, inline=False)
#             embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name + "#" +
#                                                 client.get_user(guild.owner_id).discriminator + ":" + str(
#                 guild.owner_id), inline=False)
#             embed.add_field(name="Created", value="at " +
#                                                   guild.created_at.strftime("%Y/%m/%d"), inline=False)
#             embed.set_thumbnail(url=str(guild.banner_url))
#             await msg.channel.send(embed=embed)
#     else:
#         await msg.channel.send("Unkown debug command!")
#
#
# async def sets(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     if op == "creater_role":
#         guild = msg.guild
#         if 'creater_role' in groups[guild.id]:
#             if guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#                 await msg.channel.send("クリエイターロールは既に設定されています。")
#                 return (0)
#         roles = {}
#         result = ""
#         i = 1
#         for x in guild.roles[::-1]:
#             result = result + '{0}. {1}\n'.format(i, x.name)
#             roles[i] = x.id
#             i += 1
#         embed = discord.Embed(title="Roles", description=result)
#         await msg.channel.send(embed=embed)
#
#         def check(m):
#             return m.author == msg.author and m.channel == msg.channel
#
#         try:
#             m = await client.wait_for("message", timeout=10.0, check=check)
#         except asyncio.TimeoutError:
#             await msg.channel.send("Time outed!")
#         else:
#             if int(m.content) in roles:
#                 groups[guild.id]['creater_role'] = roles[int(m.content)]
#                 await msg.channel.send(guild.get_role(roles[int(m.content)]).name + "をクリエイターロールに設定しました。")
#             else:
#                 await msg.channel.send("誤ったリアクションです！")
#     elif op == "vc_categories":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             categories = command[1]
#             if categories not in list(map(lambda x: x.name, guild.categories)):
#                 await msg.channel.send("カテゴリ" + categories + "は存在しません。")
#                 return (0)
#             groups[msg.guild.id]['vc_categories'] = msg.content[18:]
#             await msg.channel.send(msg.content[18:] + "をVCカテゴリに設定しました。")
#     elif op == "req_categories":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             categories = command[1]
#             if categories not in list(map(lambda x: x.name, guild.categories)):
#                 await msg.channel.send("カテゴリ" + categories + "は存在しません。")
#                 return (0)
#             groups[msg.guild.id]['req_categories'] = msg.content[19:]
#             await msg.channel.send(msg.content[19:] + "をrequestカテゴリに設定しました。")
#     elif op == "req_ad_categories":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             categories = command[1]
#             if categories not in list(map(lambda x: x.name, guild.categories)):
#                 await msg.channel.send("カテゴリ" + categories + "は存在しません。")
#                 return (0)
#             groups[msg.guild.id]['req_ad_categories'] = msg.content[22:]
#             await msg.channel.send(msg.content[22:] + "をリクエスト(admin)カテゴリに設定しました。")
#     elif op == "thread_name":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             if 'thread' not in groups[guild.id]:
#                 groups[guild.id]['thread'] = {'threads': {}}
#             name = command[1]
#             groups[guild.id]['thread']['thread_name'] = name
#             await msg.channel.send(name + "をスレッドネームに設定しました。")
#     elif op == "thread_categories":
#         guild = msg.guild
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         else:
#             if 'thread' not in groups[guild.id]:
#                 groups[guild.id]['thread'] = {'threads': {}}
#             categories = command[1]
#             if categories not in list(map(lambda x: x.name, guild.categories)):
#                 await msg.channel.send("カテゴリ" + categories + "は存在しません。")
#                 return (0)
#             groups[msg.guild.id]['thread']['thread_categories'] = msg.content[22:]
#             await msg.channel.send(msg.content[22:] + "をスレッドカテゴリに設定しました。")
#     else:
#         await msg.channel.send("存在しないsetコマンドです。")
#
#
# async def vc(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     if op == "create":
#         guild = msg.guild
#         if 'creater_role' not in groups[guild.id]:
#             await msg.channel.send("先に、クリエイターロールをセットしてください。")
#             return (0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
#             return (0)
#         elif 'vc_categories' not in groups[guild.id]:
#             await msg.channel.send("先にVCカテゴリを設定してください。")
#             return (0)
#         else:
#             ch = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(
#                 groups[guild.id]['vc_categories'])].create_voice_channel("➕ 新規作成[" + msg.content[10:] + "]")
#             if 'vc_ch' in groups[msg.guild.id]:
#                 groups[msg.guild.id]['vc_ch'][ch.id] = {
#                     'kind': 'ROOT', 'name': msg.content[10:], 'leafs': [], 'root': None}
#             else:
#                 groups[msg.guild.id]['vc_ch'] = {}
#                 groups[msg.guild.id]['vc_ch'][ch.id] = {
#                     'kind': 'ROOT', 'name': msg.content[10:], 'leafs': [], 'root': None}
#             await msg.channel.send("作成しました！")
#     else:
#         await msg.channel.send("存在しないvcコマンドです。")
#
#
# async def thread(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     if op == "create":
#         guild = msg.guild
#         if 'thread' not in groups[guild.id]:
#             groups[guild.id]['thread'] = {'threads': {}}
#         if 'thread_categories' not in groups[guild.id]['thread']:
#             await msg.channel.send("先にスレッドカテゴリを設定してください。")
#             return (0)
#         elif 'thread_name' not in groups[guild.id]['thread']:
#             await msg.channel.send("先にスレッドネームを設定してください。")
#             return (0)
#         else:
#             if 'threads' not in groups[guild.id]['thread']:
#                 groups[guild.id]['thread']['threads'] = {}
#             categories = guild.categories[
#                 list(map(lambda x: x.name, guild.categories)).index(groups[guild.id]['thread']['thread_categories'])]
#             num = len(groups[guild.id]['thread']['threads'].keys())
#             ch = await categories.create_text_channel(
#                 str(num) + ". 【" + groups[guild.id]['thread']['thread_name'] + "】")
#             await ch.set_permissions(msg.author, read_messages=True, send_messages=True)
#             groups[guild.id]['thread']['threads'][ch.id] = msg.author.id
#             await msg.channel.send("作成しました！")
#     elif op == "close":
#         guild = msg.guild
#         if msg.channel.id not in groups[guild.id]['thread']['threads'].keys():
#             await msg.channel.send("スレッドのみを削除することができます。")
#             return (0)
#         elif msg.author.id == groups[guild.id]['thread']['threads'][msg.channel.id]:
#             await guild.system_channel.send(msg.channel.name + "を削除します。")
#             await msg.channel.delete()
#         elif guild.get_role(groups[guild.id]['creater_role']) in msg.author.roles:
#             await guild.system_channel.send(msg.channel.name + "を削除します。")
#             await msg.channel.delete()
#         else:
#             await guild.system_channel.send("このコマンドは、スレッドの作成者もしくはクリエイターのみが実行できるコマンドです。")
#     else:
#         await msg.channel.send("存在しないvcコマンドです。")
#
#
# client.run(TOKEN)
#
# """ MEMO
#
# {
#     'group_id': ID,
#     'group_name': NAME,
#     'vc': {
#         'CH_ID': {
#         'kind': 'ROOT_OR_LEAF',
#         'name': 'NAME',
#         'leafs': [LEAFS]|NONE,
#         'root': 'ROOT_ID'|NONE,
#         'text': 'TEXT_CHANNEL_ID'
#       },
#     },
#     'sets': {
#         'XXXXX': 'XXXXX',
#     }
# }
#
#
# {
#   "GROUP_ID": {
#     'vc_ch': {
#       'CH_ID': {
#         'kind': 'ROOT_OR_LEAF',
#         'name': 'NAME',
#         'leafs': [LEAFS]|NONE,
#         'root': 'ROOT_ID'|NONE,
#         'text': 'TEXT_CHANNEL_ID'
#       }
#     },
#     'reaction_msgs': {
#         'msg_id': ['emoji','role_id']
#     },
#     'thread': {
#         'thread_name': '依頼',
#         'thread_categories': 'カテゴリ',
#         'thread_role': ROLE_ID,
#         'threads': {
#             'channel_ID': 'author'
#         }
#     }
#   }
# }
#
# """

# """
