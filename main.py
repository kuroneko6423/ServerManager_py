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


load_dotenv()
TOKEN = os.environ["TOKEN"]
servers_db = TinyDB('servers.json')
groups = {}
client = discord.Client()

@client.event
async def on_message(msg):
    global groups
    if msg.author.bot:
        return
    if msg.content == "/help":
        await helps(msg, client, groups)
        return 0
    op = msg.content.split('/', 1)[0]
    if op == "debug":
        await debug(msg, client, groups)
    elif op == "vc":
        await vc(msg, client, groups)
    elif op == "set":
        await sets(msg, client, groups)
    elif op == "mng":
        # await mng(msg, client, groups)
        await msg.channel.send("未対応の機能です")
    elif op == "role":
        await role(msg, client, groups)
        # await msg.channel.send("mi")
    # elif op == "ytb":
    #     await msg.channel.send("未対応の機能です")
    #     # await youtube(msg, client, groups)
    # elif op == "twt":
    #     await msg.channel.send("未対応の機能です。")
    elif op=="req":
        await request(msg, client, groups)
    elif op=="msg":
        await sysmsg(msg, client, groups)
    # elif op == "admin":
    #     pass
    # else:
    #     await msg.channel.send("Unknown op!")



@client.event
async def on_voice_state_update(member, before, after):
    global groups
    if before.channel==None:
        guild = after.channel.guild
    else:
        guild = before.channel.guild
    await guild.system_channel.send('{0} moved from {1} to {2}'.format(member, before.channel, after.channel))
    # print('{0} moved from {1} to {2}'.format(member, before.channel, after.channel))
    if before.channel != None:
        if before.channel.members == []:
            if before.channel.id in groups[guild.id]['vc_ch']:
                if groups[guild.id]['vc_ch'][before.channel.id]['kind'] == 'LEAF':
                    await guild.system_channel.send('{0} is deleted because the number of {0}s is now 0.'.format(before.channel.name))
                    v = groups[guild.id]['vc_ch'].pop(before.channel.id)
                    groups[guild.id]['vc_ch'][v['root']]['leafs'].remove(before.channel.id)
                    await before.channel.delete()
                    await client.get_channel(v['text']).delete()
    if after.channel != None:
        if after.channel.id in groups[guild.id]['vc_ch']:
            if groups[guild.id]['vc_ch'][after.channel.id]['kind'] == 'ROOT':
                ch = await guild.categories[list(map(lambda x: x.name, after.channel.guild.categories)).index(groups[guild.id]['vc_categories'])].create_voice_channel('No.{0} [{1}]'.format(len(groups[guild.id]['vc_ch'][after.channel.id]['leafs'])+1, groups[guild.id]['vc_ch'][after.channel.id]['name']))
                ch_text = await guild.categories[list(map(lambda x: x.name, after.channel.guild.categories)).index(groups[guild.id]['vc_categories'])].create_text_channel('{1}_{0}'.format(len(groups[guild.id]['vc_ch'][after.channel.id]['leafs'])+1, groups[guild.id]['vc_ch'][after.channel.id]['name']))
                groups[guild.id]['vc_ch'][ch.id] = {'kind': 'LEAF', 'name': groups[guild.id]['vc_ch'][after.channel.id]['name'], 'leafs': None, 'root': after.channel.id, 'text': ch_text.id}
                groups[guild.id]['vc_ch'][after.channel.id]['leafs'].append(ch.id)
                await member.move_to(ch)


async def logs(msg, guild=None, cmd_msg=True):
    global groups
    if guild is None:
        print('[{0}]{1}'.format(time.time(), msg))
    else:
        if cmd_msg:
            print('[{0}][{1}:{2}]{3}'.format(
                time.time(), guild.name, guild.id, msg))
        if guild.system_channel is None:
            pass
        else:
            await guild.system_channel.send('[{0}]{1}'.format(str(time.time()), msg))


@tasks.loop(seconds=10)
async def db_save():
    global groups
    que = Query()
    servers_db.update({'data': groups}, que.id == 0)
    await logs("DB saved.")
    # for x in client.guilds:
    #     await logs("DB saved.", x, False)


@client.event
async def on_ready():
    global groups
    for x in client.guilds:
        await logs("Bot is ready!", x, False)
    await logs("Bot is ready!")


@client.event
async def on_connect():
    global groups
    for x in client.guilds:
        await logs("Bot has logged in!", x, False)
    await logs("Bot has logged in!")
    que = Query()
    temp_groups = servers_db.search(que.id == 0)[0]['data']
    groups = {}
    for k,v in temp_groups.items():
        groups[int(k)]=v
    vc_ch = {}
    for k,v in groups.items():
        for k2,v2 in groups[k]["vc_ch"].items():
            vc_ch[int(k2)]=v2
        groups[k]["vc_ch"]=vc_ch
    db_save.start()
    client.change_presence(activity=discord.CustomActivity(str(len(client.guilds))+"個のサーバで稼働中"))


@client.event
async def on_disconnect():
    global groups
    for x in client.guilds:
        await logs("Bot has been logged out!", x, False)
    await logs("Bot has been logged out!")


@client.event
async def on_guild_join(guild):
    global groups
    groups[guild.id] = {}
    embed = discord.Embed(
    title="Hi!", description="I'm a server management bot!\nAnd if you don't know how to use it, just say '/help`!", color=discord.Colour.red())
    await guild.system_channel.send(embed=embed)
    client.change_presence(activity=CustomActivity(str(len(client.guilds)+"個のサーバで稼働中"))


# @client.event
# async def on_raw_reaction_add(payload):
#     global groups
#     guild = client.get_guild(payload.guild_id)
#     if str(payload.message_id) in groups[guild.id]['reaction_msgs']:
#         if str(payload.emoji) == groups[guild.id]['reaction_msgs'][payload.message_id][0]:
#             await client.get_user(payload.user_id).add_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][payload.message_id][1])))

@client.event
async def on_reaction_add(reaction, user):
    print("a")
    global groups
    print("a")
    guild = reaction.message.guild
    print("a")
    if str(reaction.message.id) in groups[guild.id]['reaction_msgs'].keys():
        print("a")
        if str(reaction.emoji) == groups[guild.id]['reaction_msgs'][str(reaction.message.id)][0]:
            print("a")
            await user.add_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][str(reaction.message.id)][1])))
            print("a")

# @client.event
# async def on_raw_reaction_remove(payload):
#     global groups
#     guild = client.get_guild(payload.guild_id)
#     if str(payload.message_id) in groups[guild.id]['reaction_msgs']:
#         if str(payload.emoji) == groups[guild.id]['reaction_msgs'][reaction.message.id][0]:
#             await client.get_user(payload.user_id).remove_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][reaction.message.id][1])))


# async def mng(msg, client, groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     guild = msg.guild
#     if op == "ban":
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("Please set creater's role!")
#             return(0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("It's only creater's command!")
#             return(0)
#         for x in msg.raw_mentions():
#             await msg.guild.ban(client.get_user(x))
#             await msg.channel.send("Baned")
#     elif op == "unban":
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("Please set creater's role!")
#             return(0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("It's only creater's command!")
#             return(0)
#         for x in msg.raw_mentions():
#             await msg.guild.unban(client.get_user(x))
#             await msg.channel.send("Unbaned")
#     elif op == "kick":
#         if 'creater_role' not in groups[msg.guild.id]:
#             await msg.channel.send("Please set creater's role!")
#             return(0)
#         elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
#             await msg.channel.send("It's only creater's command!")
#             return(0)
#         print(str(msg.raw_mentions()))
#         for x in msg.raw_mentions():
#             await msg.guild.kick(client.get_user(x))
#             await msg.channel.send("Kicked")
#     else:
#         await msg.channel.send("Unknown mng command!")


# async def youtube(msg,client,groups):
#     command = msg.content.split('/', 1)[1].split(' ')
#     op = command[0]
#     guild = msg.guild
#     if 'youtube_ch' not in groups[guild.id].keys():
#         groups[guild.id]['youtube_ch']={}
#     if op=="set":
#         groups[guild.id]['youtube_ch'][str(command[1])]=''
#         await msg.channel.send("Created")
#     elif op=="remove":
#         groups[guild.id]['youtube_ch'].pop(str(command[1]))
#         await msg.channel.send("Removed")
#     elif op=="lists":
#         await msg.channel.send("".join(list(map(lambda x: str(x)+"\n",groups[guild.id]['youtube_ch'].keys()))))
#     else:
#         await msg.channel.send("Unkown youtube command!")

async def sysmsg(msg,client,groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    guild = msg.guild
    if op=="create":
        if msg.author==431707293692985344:
            for x in client.guilds:
                await x.system_channel.send(command[1])
                await msg.channel.send("Sended to "+x.name)
        else:
            await msg.channel.send("")
    else:
        await msg.channel.send("Unkown msg command!")

async def request(msg, client, groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    guild = msg.guild
    if op == "create":
        guild = msg.guild
        ch = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(groups[guild.id]['req_categories'])].create_text_channel("Request【"+msg.content[11:]+"】")
        ch2 = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(groups[guild.id]['req_ad_categories'])].create_text_channel("Request Admin【"+msg.content[11:]+"】")
        await msg.channel.send("Created!")
    elif op=="close":
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        await msg.channel.delete()
    else:
        await msg.channel.send("Unknown req command!")

async def role(msg, client, groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    guild = msg.guild
    if op == "create":
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        roles = {}
        result = ""
        i = 1
        for x in guild.roles[::-1]:
            result = result+'{0}. {1}\n'.format(i, x.name)
            roles[i] = x.id
            i += 1
        embed = discord.Embed(title="Roles", description=result)
        await msg.channel.send(embed=embed)

        def check(m):
            return m.author == msg.author and m.channel == msg.channel

        try:
            m = await client.wait_for("message", timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await msg.channel.send("Time outed!")
        else:
            await msg.channel.send("対象にする絵文字を入力してください。")
            try:
                m2 = await client.wait_for("message", timeout=10.0, check=check)
            except asyncio.TimeoutError:
                await msg.channel.send("Time outed!")
            else:
                await msg.channel.send("Emojiを"+m2.content+"に登録しました。")
                msg = await msg.channel.send("このメッセージにリアクション"+m2.content+"を付与すると、ロール"+guild.get_role(roles[int(m.content)]).name+"が付与されます。")
                await msg.add_reaction(m2.content)
                if 'reaction_msgs' not in groups[guild.id]:
                    groups[guild.id]["reaction_msgs"] = {}
                groups[guild.id]["reaction_msgs"][str(msg.id)] = [m2.content, roles[int(m.content)]]
    else:
        await msg.channel.send("Unkown role command!")


async def helps(msg, client, groups):
    embed2 = discord.Embed(title="Help", description="")
    embed2.add_field(name="Debug Command", value=(
        "`debug/profile Mention` メンションされた人のプロフィールを表示します.\n"
        "`debug/profile UserID` ID指定された人のプロフィールを表示します.\n"
        "`debug/info` サーバーの詳細を表示します"
        "`debug/info ServerID` コマンドを実行した人のプロフィールを表示します。"
    ), inline=False)
    embed2.add_field(name="Voice Chat Command", value=(
        "`vc/create` 普遍的なボイスチャンネルを作成します"
    ), inline=False)
    embed2.add_field(name="Role setup Command", value=(
        "`role/create` リアクションをつけるとロール付与されるメッセージを作成します。"
    ), inline=False)
    embed2.add_field(name="Setting Command", value=(
        "`set/creater_role` クリエイターロールを設定します。設定することにより、クリエイターしかコマンドを実行できなくなります。\n"
        "`set/vc_categories <カテゴリ名>` VCを作成するカテゴリを指定します。\n"
        "`set/req_categories <カテゴリ名>` リクエストを作成するカテゴリを指定します。\n"
        "`set/req_ad_categories <カテゴリ名>` リクエスト(admin)を作成するカテゴリを指定します。\n"
    ), inline=False)
    embed2.add_field(name="Manage Command", value=(
        "`mng/ban <Mention>` Ban\n"
        "`mng/kick <Mention>` Kick.\n"
        "`mng/unban <Mention>` Unban\n"
        "`mng/bans` Show listed bans."
    ), inline=False)
    embed2.add_field(name="Request Manege Command", value=(
        "`req/create <title>` 新規リクエストを作成します。\n"
        "`req/close` リクエストを終了します。\n"
    ), inline=False)
    # embed2.add_field(name="Youtube&Twitter Command", value=(
    #     "`youtube/set <YoutubeのチャンネルのURL>` チャンネルにアップロードをした際に、通知をします。\n"
    #     "`twitter/set <TwitterのID>` Tweetをした際に、通知をします。\n"
    #     "`youtube/remove <YoutubeのチャンネルのURL>` チャンネルを通知リストから削除します。\n"
    #     "`twitter/remove <TwitterのID>` アカウントを通知リストから削除します。\n"
    #     # "`mng/bans` Show listed bans."
    # ), inline=False)
    embed2.add_field(name="Help Center", value=("以下のURLに詳しい説明が載っています。是非ご参照ください。\nhttps://qiita.com/k439_/items/96b8a832642ace52b148"))
#   embed.add_field(name="System Command ( Only use cronちゃん )",value=(
#     "`sys/save`\n"
#     "`sys/load`"
#     ),inline=False)
    await msg.channel.send(embed=embed2)


async def debug(msg, client, groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    if op == "profile":
        if msg.raw_mentions != []:
            for user_id in msg.raw_mentions:
                user = msg.guild.get_member(user_id)
                embed = discord.Embed(
                    title=(user.name+"#"+user.discriminator), description=str(user.id))
                embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
                    "%Y/%m/%d"), inline=False)
                embed.add_field(name="NickName", value=user.nick, inline=False)
                embed.add_field(name="Status", value=user.status, inline=False)
                embed.add_field(name="Roles", value="\n".join(
                    map(lambda x: x.name+":"+str(x.id), user.roles)), inline=False)
                embed.add_field(name="Top Role", value=user.top_role.name +
                                ":"+str(user.top_role.id), inline=False)
                embed.add_field(name="Display Name",
                                value=user.display_name, inline=False)
                embed.add_field(name="Activity",
                                value=user.activity, inline=False)
                embed.set_thumbnail(url=str(user.avatar_url))
                await msg.channel.send(embed=embed)
        elif command[1:] != []:
            for user_id in command[1:]:
                user = msg.guild.get_member(int(user_id))
                embed = discord.Embed(
                    title=(user.name+"#"+user.discriminator), description=str(user.id))
                embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
                    "%Y/%m/%d"), inline=False)
                embed.add_field(name="NickName", value=user.nick, inline=False)
                embed.add_field(name="Status", value=user.status, inline=False)
                embed.add_field(name="Roles", value="\n".join(
                    map(lambda x: x.name+":"+str(x.id), user.roles)), inline=False)
                embed.add_field(name="Top Role", value=user.top_role.name +
                                ":"+str(user.top_role.id), inline=False)
                embed.add_field(name="Display Name",
                                value=user.display_name, inline=False)
                embed.add_field(name="Activity",
                                value=user.activity, inline=False)
                embed.set_thumbnail(url=str(user.avatar_url))
                await msg.channel.send(embed=embed)
        else:
            user = msg.author
            embed = discord.Embed(
                title=(user.name+"#"+user.discriminator), description=str(user.id))
            embed.add_field(name="JOINED_AT", value=user.joined_at.strftime(
                "%Y/%m/%d"), inline=False)
            embed.add_field(name="NickName", value=user.nick, inline=False)
            embed.add_field(name="Status", value=user.status, inline=False)
            embed.add_field(name="Roles", value="\n".join(
                map(lambda x: x.name+":"+str(x.id), user.roles)), inline=False)
            embed.add_field(name="Top Role", value=user.top_role.name +
                            ":"+str(user.top_role.id), inline=False)
            embed.add_field(name="Display Name",
                            value=user.display_name, inline=False)
            embed.add_field(name="Activity", value=user.activity, inline=False)
            embed.set_thumbnail(url=str(user.avatar_url))
            await msg.channel.send(embed=embed)
    elif op == "info":
        if command[1:] != []:
            for guild_id in command[1:]:
                guild = client.get_guild(int(guild_id))
                embed = discord.Embed(
                    title=guild.name+":"+str(guild.id), description=guild.description)
                embed.add_field(
                    name="Emojis", value=guild.emojis, inline=False)
                embed.add_field(
                    name="Region", value=guild.region, inline=False)
                embed.add_field(name="AFK", value="TimeOut: "+str(guild.afk_timeout) +
                                "\nChannel:"+str(guild.afk_channel), inline=False)
                embed.add_field(name="Icon", value=guild.icon, inline=False)
                embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name+"#" +
                                client.get_user(guild.owner_id).discriminator+":"+str(guild.owner_id), inline=False)
                embed.add_field(name="Created", value="at " +
                                guild.created_at.strftime("%Y/%m/%d"), inline=False)
                embed.set_thumbnail(url=str(guild.banner_url))
                await msg.channel.send(embed=embed)
        else:
            guild = msg.guild
            embed = discord.Embed(title=guild.name+":" +
                                  str(guild.id), description=guild.description)
            embed.add_field(name="Emojis", value=guild.emojis, inline=False)
            embed.add_field(name="Region", value=guild.region, inline=False)
            embed.add_field(name="AFK", value="TimeOut: "+str(guild.afk_timeout) +
                            "\nChannel:"+str(guild.afk_channel), inline=False)
            embed.add_field(name="Icon", value=guild.icon, inline=False)
            embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name+"#" +
                            client.get_user(guild.owner_id).discriminator+":"+str(guild.owner_id), inline=False)
            embed.add_field(name="Created", value="at " +
                            guild.created_at.strftime("%Y/%m/%d"), inline=False)
            embed.set_thumbnail(url=str(guild.banner_url))
            await msg.channel.send(embed=embed)
    else:
        await msg.channel.send("Unkown debug command!")


async def sets(msg, client, groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    if op == "creater_role":
        guild = msg.guild
        if 'creater_role' in groups[guild.id]:
            if guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
                await msg.channel.send("Creater's role is already registered.")
                return(0)
        roles = {}
        result = ""
        i = 1
        for x in guild.roles[::-1]:
            result = result+'{0}. {1}\n'.format(i, x.name)
            roles[i] = x.id
            i += 1
        embed = discord.Embed(title="Roles", description=result)
        await msg.channel.send(embed=embed)

        def check(m):
            return m.author == msg.author and m.channel == msg.channel

        try:
            m = await client.wait_for("message", timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await msg.channel.send("Time outed!")
        else:
            if int(m.content) in roles:
                groups[guild.id]['creater_role'] = roles[int(m.content)]
                await msg.channel.send(guild.get_role(roles[int(m.content)]).name+" has been registered as the role of creator.")
            else:
                await msg.channel.send("Unknown reaction!")
    elif op == "vc_categories":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        else:
            categories = command[1]
            if categories not in list(map(lambda x: x.name,guild.categories)):
                await msg.channel.send("Unkown categorie "+categories)
                return(0)
            groups[msg.guild.id]['vc_categories'] = msg.content[18:]
            await msg.channel.send("I set "+msg.content[18:]+" to the voice chat category.")
    elif op == "req_categories":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        else:
            categories = command[1]
            if categories not in list(map(lambda x: x.name,guild.categories)):
                await msg.channel.send("Unkown categorie "+categories)
                return(0)
            groups[msg.guild.id]['req_categories'] = msg.content[19:]
            await msg.channel.send("I set "+msg.content[19:]+" to the request channel category.")
    elif op == "req_ad_categories":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("Please set creater's role!")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("It's only creater's command!")
            return(0)
        else:
            categories = command[1]
            if categories not in list(map(lambda x: x.name,guild.categories)):
                await msg.channel.send("Unkown categorie "+categories)
                return(0)
            groups[msg.guild.id]['req_ad_categories'] = msg.content[22:]
            await msg.channel.send("I set "+msg.content[22:]+" to the request admin channel category.")
    else:
        await msg.channel.send("Unkown set command!")


async def vc(msg, client, groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    if op == "create":
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
                groups[msg.guild.id]['vc_ch'][ch.id] = {
                    'kind': 'ROOT', 'name': msg.content[10:], 'leafs': [], 'root': None}
            else:
                groups[msg.guild.id]['vc_ch'] = {}
                groups[msg.guild.id]['vc_ch'][ch.id] = {
                    'kind': 'ROOT', 'name': msg.content[10:], 'leafs': [], 'root': None}
            await msg.channel.send("Created!")
    else:
        await msg.channel.send("Unknown vc command!")


client.run(TOKEN)


""" MEMO

{
    'group_id': ID,
    'group_name': NAME,
    'vc': {
        'CH_ID': {
        'kind': 'ROOT_OR_LEAF',
        'name': 'NAME',
        'leafs': [LEAFS]|NONE,
        'root': 'ROOT_ID'|NONE,
        'text': 'TEXT_CHANNEL_ID'
      },
    },
    'sets': {
        'XXXXX': 'XXXXX',
    }
}


{
  "GROUP_ID": {
    'vc_ch': {
      'CH_ID': {
        'kind': 'ROOT_OR_LEAF',
        'name': 'NAME',
        'leafs': [LEAFS]|NONE,
        'root': 'ROOT_ID'|NONE,
        'text': 'TEXT_CHANNEL_ID'
      }
    },
    'reaction_msgs': {
        'msg_id': ['emoji','role_id']
    }
  }
}

"""
