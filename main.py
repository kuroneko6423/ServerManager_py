import os
import discord
import sys
import ast
import time
import asyncio
import logging
import random
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from tinydb import TinyDB, Query
from discord.ext import tasks


load_dotenv()
TOKEN = os.environ["TOKEN"]
servers_db = TinyDB('servers.json')
groups = {}
formatter = "%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s"
logging.basicConfig(filename='logs/logger.log',format=formatter,level=logging.INFO)
client = discord.Client()
ads = [
    ["このbotをあなたのサーバに導入しませんか？","↓↓このbotの招待リンク↓↓\nhttps://discord.com/oauth2/authorize?client_id=699967735538384987&permissions=8&scope=bot\n↓↓詳しいことはこの記事に載ってるよ!↓↓\nhttps://qiita.com/k439_/items/96b8a832642ace52b148\n是非導入してみてね!"],
    ["サポートが必要ですか？","↓↓この記事を見てみよう！↓↓\nhttps://qiita.com/k439_/items/96b8a832642ace52b148\n作成者の連絡先も載ってるよ！"],
    # ["INFOの表示頻度が高すぎて、ウザい!?","↓↓このコマンドで表示頻度を設定しよう!\n`未対応です`"],
    ["バグや間違いを発見しましたか？","以下の招待リンクのdiscordグループにいるcronちゃんまでお声掛けください!\nhttps://discord.gg/AeP5att"],
    ["開発に参加したい？","以下のGithubへPull RequestやIssueなどをお願いします！\nhttps://github.com/cronree-91/ServerManager"]
    ]


# @client.event
# async def on_error(a,b):
#     type_, value, traceback_ = sys.exc_info()
#     logs("ERROR WAS HAPPEN! {0} {1}".format(str(type_),value))
#     logging.error("ERROR WAS HAPPEN! %s %s",str(type_),value)


def get_channel_from_name(guild,name):
    channels = {}
    for x in guild.channels:
        channels[x.name]=x.id
    if name in channels:
        return channels[name]
    else:
        return guild.system_channel

@client.event
async def on_message(msg):
    global groups
    if msg.author.bot:
        return
    logging.info('%s MESSAGE %s',msg.guild.id,msg.content)
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
    elif op == "role":
        await role(msg, client, groups)
    elif op=="req":
        await request(msg, client, groups)
    elif op=="admin":
        await admin(msg,client,groups)
    elif op=="th":
        await thread(msg,client,groups)
    # elif op == "mng":
        # await mng(msg, client, groups)
        # await msg.channel.send("未対応の機能です")
        # await msg.channel.send("mi")
    # elif op == "ytb":
    #     await msg.channel.send("未対応の機能です")
    #     # await youtube(msg, client, groups)
    # elif op == "twt":
    #     await msg.channel.send("未対応の機能です。")
    # else:
    #     await msg.channel.send("Unknown op!")


@client.event
async def on_voice_state_update(member, before, after):
    try:
        global groups
        if before.channel==None:
            guild = after.channel.guild
        else:
            guild = before.channel.guild
        await guild.system_channel.send('{0}が{1}から{2}へ移動しました。'.format(member, before.channel, after.channel))
        logging.info('{0} moved from {1} to {2}'.format(member, before.channel, after.channel))
        if before.channel != None:
            if before.channel.id in groups[guild.id]['vc_ch']:
                if groups[guild.id]['vc_ch'][before.channel.id]['kind'] == 'LEAF':
                    if before.channel.members == []:
                        await guild.system_channel.send('{0}を、人数が{0}人になったため、削除します。'.format(before.channel.name))
                        v = groups[guild.id]['vc_ch'].pop(before.channel.id)
                        groups[guild.id]['vc_ch'][v['root']]['leafs'].remove(before.channel.id)
                        await before.channel.delete()
                        await client.get_channel(v['text']).delete()
                    else:
                        text_ch = client.get_channel(groups[guild.id]['vc_ch'][before.channel.id]['text'])
                        await text_ch.set_permissions(member, read_messages=False,send_messages=False)
        if after.channel != None:
            if after.channel.id in groups[guild.id]['vc_ch']:
                if groups[guild.id]['vc_ch'][after.channel.id]['kind'] == 'ROOT':
                    ch = await guild.categories[list(map(lambda x: x.name, after.channel.guild.categories)).index(groups[guild.id]['vc_categories'])].create_voice_channel('No.{0} [{1}]'.format(len(groups[guild.id]['vc_ch'][after.channel.id]['leafs'])+1, groups[guild.id]['vc_ch'][after.channel.id]['name']))
                    ch_text = await guild.categories[list(map(lambda x: x.name, after.channel.guild.categories)).index(groups[guild.id]['vc_categories'])].create_text_channel('{1}_{0}'.format(len(groups[guild.id]['vc_ch'][after.channel.id]['leafs'])+1, groups[guild.id]['vc_ch'][after.channel.id]['name']))
                    await ch_text.set_permissions(guild.default_role, read_messages=False,send_messages=False)
                    groups[guild.id]['vc_ch'][ch.id] = {'kind': 'LEAF', 'name': groups[guild.id]['vc_ch'][after.channel.id]['name'], 'leafs': None, 'root': after.channel.id, 'text': ch_text.id}
                    groups[guild.id]['vc_ch'][after.channel.id]['leafs'].append(ch.id)
                    await member.move_tif  
                elif groups[guild.id]['vc_ch'][after.channel.id]['kind'] == 'LEAF':
                    text_ch = client.get_channel(groups[guild.id]['vc_ch'][after.channel.id]['text'])
                    await text_ch.set_permissions(member, read_messages=True,send_messages=True)
    except:
        logging.info('Guild: {0} VOICE_STATE_UPDATE ERROR'.format(guild.name))
        print( 'Guild: {0} VOICE_STATE_UPDATE ERROR'.format(guild.name) )


@tasks.loop(seconds=10)
async def db_save():
    global groups
    que = Query()
    servers_db.update({'data': groups}, que.id == 0)
    logging.info("DB saved")


@tasks.loop(minutes=60)
async def ad():
    global groups
    global ads
    ad = random.choice(ads)
    for x in client.guilds:
        try:
            embed = discord.Embed(title="[INFO]"+ad[0], description=ad[1], color=discord.Colour.red())
            await x.system_channel.send(embed=embed)
            print("Sended to "+str(x.name))
        except Exception as e:
            logging.info('ERROR: AD GUILD: {0}'.format(guild.name))
            print('ERROR: AD GUILD: {0}'.format(guild.name))


@client.event
async def on_ready():
    global groups
    print("Bot is ready")
    logging.info("Bot is ready!")
    print(str(len(client.guilds))+"servers | "+str(get_members())+" members")
    await client.change_presence(activity=discord.Game(str(len(client.guilds))+"servers | "+str(get_members())+" members"))
    logging.info(str(len(client.guilds))+"個のサーバで稼働中")
    ad.start()


@client.event
async def on_connect():
    global groups
    logging.info("Bot has logged in!")
    print("Bot has logged in!")
    que = Query()
    temp_groups = servers_db.search(que.id == 0)[0]['data']
    groups = {}
    for k,v in temp_groups.items():
        groups[int(k)]=v
    vc_ch = {}
    for k,v in groups.items():
        if "vc_ch" in groups[k]:
                for k2,v2 in groups[k]["vc_ch"].items():
                    vc_ch[int(k2)]=v2
                groups[k]["vc_ch"]=vc_ch
    db_save.start()


@client.event
async def on_disconnect():
    global groups
    logging.info("Bot has been logged out!")
    print("Bot has been logged out!")


@client.event
async def on_guild_join(guild):
    global groups
    groups[guild.id] = {'vc_ch':{},'reaction_msgs':{}}
    embed = discord.Embed(title="こんにちは!", description="このBOTを導入してくださってありがとうございます。\nまずは、最初に`/help`と話しかけてみましょう!", color=discord.Colour.red())
    await guild.system_channel.send(embed=embed)
    print(str(len(client.guilds))+"servers | "+str(get_members()+" members"))
    await client.change_presence(activity=discord.Game(str(len(client.guilds))+"servers | "+str(get_members())+" members"))
    logging.info("Guild joined")

def get_members():
    result = 0
    for x in client.guilds:
        try:
            members = int(len(x.members))
            print(x.name)
            print(members)
            result+=members
        except Exception as e:
            print("except!!")
    return result


@client.event
async def on_reaction_add(reaction, user):
    global groups
    guild = reaction.message.guild
    if 'reaction_msgs' not in groups[guild.id]:
        groups[guild.id]['reaction_msgs']={}
    if str(reaction.message.id) in groups[guild.id]['reaction_msgs'].keys():
        if str(reaction.emoji) == groups[guild.id]['reaction_msgs'][str(reaction.message.id)][0]:
            await user.add_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][str(reaction.message.id)][1])))


@client.event
async def on_reaction_remove(reaction, user):
    global groups
    guild = reaction.message.guild
    if str(reaction.message.id) in groups[guild.id]['reaction_msgs'].keys():
        if str(reaction.emoji) == groups[guild.id]['reaction_msgs'][str(reaction.message.id)][0]:
            await user.remove_roles(guild.get_role(int(groups[guild.id]['reaction_msgs'][str(reaction.message.id)][1])))


async def admin(msg,client,groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    guild = msg.guild
    logging.warning("Admin command %s by %s",msg.content,msg.author.id)
    if msg.author.id!=431707293692985344:
        await msg.channel.send("このコマンドは、cronちゃんのみが使用できるBOT管理者用コマンドです。")
        return(0)
    if op=="msg_create":
        if msg.author.id==431707293692985344:
            for x in client.guilds:
                channels={}
                try:
                    # for x2 in guild.channels:
                    #     channels[x2.name]=x2
                    # if 'お知らせ' in channels.keys():
                    #     await channels['お知らせ'].send(command[1])
                    #     await msg.channel.send("Sended to "+x.name +" in "+channels['お知らせ'].name)
                    # else:
                    #     await x.system_channel.send(command[1])
                    #     await msg.channel.send("Sended to "+x.name+" in "+x.system_channel.name)
                    ch = guild.system_channel
                    tmp = guild.system_channel

                    tmp = get_channel_from_name(guild,"お知らせ")
                    if tmp!=ch:
                        ch = tmp
                    else:
                        tmp = get_channel_from_name(guild,"おしらせ")
                        if tmp!=ch:
                            ch = tmp
                        else:
                            if guild.text_channels[0] is not None:
                                ch = guild.text_channels[0]
                    
                    if ch is not None:
                        await x.system_channel.send(" ".join(command[1:]))
                        await msg.channel.send("Sended to `"+x.name+"` in `"+ch.name+"`")
                except Exception as e:
                    print(e)
    elif op=="show_groups":
        if msg.author.id==431707293692985344:
            await msg.channel.send(file=discord.File("servers.json",filename="servers.json"))
    elif op=="logs":
        if msg.author.id==431707293692985344:
            await msg.channel.send(file=discord.File("logs/logger.log",filename="logger.log"))
            res = subprocess.check_output(['tail', 'logs/logger.log'])
            await msg.channel.send(str(res).replace('\\n','\n'))
    # elif op=="program":
    #     if msg.author.id==431707293692985344:
    elif op=="invgr":
        guilds = client.guilds
        for x in guilds:
            try:
                guild = x
                embed = discord.Embed(title=guild.name+":" +str(guild.id), description=guild.description)
                embed.add_field(name="Emojis", value=guild.emojis, inline=False)
                embed.add_field(name="Region", value=guild.region, inline=False)
                embed.add_field(name="AFK", value="TimeOut: "+str(guild.afk_timeout) +
                                "\nChannel:"+str(guild.afk_channel), inline=False)
                embed.add_field(name="Icon", value=guild.icon, inline=False)
                embed.add_field(name="Owner", value=client.get_user(guild.owner_id).name+"#" +
                                client.get_user(guild.owner_id).discriminator+":"+str(guild.owner_id), inline=False)
                invite = await guild.invites()
                invites = list(map(lambda x: str(x),invite))
                embed.add_field(name="Invite", value=invites, inline=False)
                embed.add_field(name="Created", value="at " +
                                guild.created_at.strftime("%Y/%m/%d"), inline=False)
                embed.set_thumbnail(url=str(guild.banner_url))
                await msg.channel.send(embed=embed)
            except Exception as e:
                print(e)
 
    else:
        await msg.channel.send("存在しないadminコマンドです。")

async def request(msg, client, groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    guild = msg.guild
    if op == "create":
        guild = msg.guild
        ch = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(groups[guild.id]['req_categories'])].create_text_channel("Request【"+msg.content[11:]+"】")
        ch2 = await guild.categories[list(map(lambda x: x.name, guild.categories)).index(groups[guild.id]['req_ad_categories'])].create_text_channel("Request Admin【"+msg.content[11:]+"】")
        await msg.channel.send("作成しました。")
    elif op=="close":
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("先に、クリエイターロールをセットしてください。")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
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
            await msg.channel.send("先に、クリエイターロールをセットしてください。")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
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
    # embed2.add_field(name="Debug Command", value=(
    #     "`debug/profile Mention` メンションされた人のプロフィールを表示します.\n"
    #     "`debug/profile UserID` ID指定された人のプロフィールを表示します.\n"
    #     "`debug/info` サーバーの詳細を表示します"
    #     "`debug/info ServerID` コマンドを実行した人のプロフィールを表示します。"
    # ), inline=False)
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
        "`set/thread_categories <カテゴリ名>` スレッドを作成するカテゴリを指定します。\n"
        "`set/thread_name <スレッド名>` スレッドの名前を指定します。\n"
    ), inline=False)
    embed2.add_field(name="Request Manege Command", value=(
        "`req/create <title>` 新規リクエストを作成します。\n"
        "`req/close` リクエストを終了します。\n"
    ), inline=False)
    embed2.add_field(name="Admin Command", value=(
        "`admin/msg_create` Server Managerが参加している全てのギルドへメッセージを一斉送信します。\n"
        "`admin/show_groups` 変数'groups'を表示します。\n"
        "`admin/logs` 直近のlogs10行とlogsファイルを表示します。"
    ), inline=False)
    embed2.add_field(name="Thread Command", value=(
        "`th/create` スレッドを新たに作成します。\n"
        "`th/close` 変数'groups'を表示します。\n"
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
            embed = discord.Embed(title=guild.name+":" +str(guild.id), description=guild.description)
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
                await msg.channel.send("クリエイターロールは既に設定されています。")
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
                await msg.channel.send(guild.get_role(roles[int(m.content)]).name+"をクリエイターロールに設定しました。")
            else:
                await msg.channel.send("誤ったリアクションです！")
    elif op == "vc_categories":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("先に、クリエイターロールをセットしてください。")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
            return(0)
        else:
            categories = command[1]
            if categories not in list(map(lambda x: x.name,guild.categories)):
                await msg.channel.send("カテゴリ"+categories+"は存在しません。")
                return(0)
            groups[msg.guild.id]['vc_categories'] = msg.content[18:]
            await msg.channel.send(msg.content[18:]+"をVCカテゴリに設定しました。")
    elif op == "req_categories":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("先に、クリエイターロールをセットしてください。")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
            return(0)
        else:
            categories = command[1]
            if categories not in list(map(lambda x: x.name,guild.categories)):
                await msg.channel.send("カテゴリ"+categories+"は存在しません。")
                return(0)
            groups[msg.guild.id]['req_categories'] = msg.content[19:]
            await msg.channel.send(msg.content[19:]+"をrequestカテゴリに設定しました。")
    elif op == "req_ad_categories":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("先に、クリエイターロールをセットしてください。")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
            return(0)
        else:
            categories = command[1]
            if categories not in list(map(lambda x: x.name,guild.categories)):
                await msg.channel.send("カテゴリ"+categories+"は存在しません。")
                return(0)
            groups[msg.guild.id]['req_ad_categories'] = msg.content[22:]
            await msg.channel.send(msg.content[22:]+"をリクエスト(admin)カテゴリに設定しました。")
    elif op == "thread_name":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("先に、クリエイターロールをセットしてください。")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
            return(0)
        else:
            if 'thread' not in groups[guild.id]:
                groups[guild.id]['thread'] = {'threads':{}}
            name = command[1]
            groups[guild.id]['thread']['thread_name'] = name
            await msg.channel.send(name+"をスレッドネームに設定しました。")
    elif op == "thread_categories":
        guild = msg.guild
        if 'creater_role' not in groups[msg.guild.id]:
            await msg.channel.send("先に、クリエイターロールをセットしてください。")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
            return(0)
        else:
            if 'thread' not in groups[guild.id]:
                groups[guild.id]['thread'] = {'threads':{}}
            categories = command[1]
            if categories not in list(map(lambda x: x.name,guild.categories)):
                await msg.channel.send("カテゴリ"+categories+"は存在しません。")
                return(0)
            groups[msg.guild.id]['thread']['thread_categories'] = msg.content[22:]
            await msg.channel.send(msg.content[22:]+"をスレッドカテゴリに設定しました。")
    else:
        await msg.channel.send("存在しないsetコマンドです。")


async def vc(msg, client, groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    if op == "create":
        guild = msg.guild
        if 'creater_role' not in groups[guild.id]:
            await msg.channel.send("先に、クリエイターロールをセットしてください。")
            return(0)
        elif guild.get_role(groups[guild.id]['creater_role']) not in msg.author.roles:
            await msg.channel.send("これは、クリエイターのみが実行できるコマンドです。")
            return(0)
        elif 'vc_categories' not in groups[guild.id]:
            await msg.channel.send("先にVCカテゴリを設定してください。")
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
            await msg.channel.send("作成しました！")
    else:
        await msg.channel.send("存在しないvcコマンドです。")

async def thread(msg, client, groups):
    command = msg.content.split('/', 1)[1].split(' ')
    op = command[0]
    if op == "create":
        guild = msg.guild
        if 'thread' not in groups[guild.id]:
            groups[guild.id]['thread'] = {'threads':{}}
        if 'thread_categories' not in groups[guild.id]['thread']:
            await msg.channel.send("先にスレッドカテゴリを設定してください。")
            return(0)
        elif 'thread_name' not in groups[guild.id]['thread']:
            await msg.channel.send("先にスレッドネームを設定してください。")
            return(0)
        else:
            if 'threads' not in groups[guild.id]['thread']:
                groups[guild.id]['thread']['threads'] = {}
            categories = guild.categories[list(map(lambda x: x.name, guild.categories)).index(groups[guild.id]['thread']['thread_categories'])]
            num = len(groups[guild.id]['thread']['threads'].keys())
            ch = await categories.create_text_channel(str(num)+". 【"+groups[guild.id]['thread']['thread_name']+"】")
            await ch.set_permissions(msg.author, read_messages=True,send_messages=True)
            groups[guild.id]['thread']['threads'][ch.id]=msg.author.id
            await msg.channel.send("作成しました！")
    elif op=="close":
        guild = msg.guild
        if msg.channel.id not in groups[guild.id]['thread']['threads'].keys():
            await msg.channel.send("スレッドのみを削除することができます。")
            return(0)
        elif msg.author.id == groups[guild.id]['thread']['threads'][msg.channel.id]:
            await guild.system_channel.send(msg.channel.name+"を削除します。")
            await msg.channel.delete()
        elif guild.get_role(groups[guild.id]['creater_role']) in msg.author.roles:
            await guild.system_channel.send(msg.channel.name+"を削除します。")
            await msg.channel.delete()
        else:
            await guild.system_channel.send("このコマンドは、スレッドの作成者もしくはクリエイターのみが実行できるコマンドです。")
    else:
        await msg.channel.send("存在しないvcコマンドです。")


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
    },
    'thread': {
        'thread_name': '依頼',
        'thread_categories': 'カテゴリ',
        'thread_role': ROLE_ID,
        'threads': {
            'channel_ID': 'author'
        }
    }
  }
}

"""
