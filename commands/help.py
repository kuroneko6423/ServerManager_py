import discord


async def cmd_help(msg, client, db, config):
    guild = msg.guild
    lang = db[guild.id]['lang']
    embed = discord.Embed(title=config['msg'][lang]['help']['title'], description=config['msg'][lang]['help']['description'])

    for x in config['msg'][lang]['help']:
        if x is not "title":
            embed.add_field(name=config['msg'][lang]['help'][x]['title'], value=(
                "¥n".join(config['msg'][lang]['help'][x]['value'])
            ), inline=False)
    await msg.channel.send(embed=embed)

    # embed.add_field(name="Voice Chat Command", value=(
    #     "`vc/create` 普遍的なボイスチャンネルを作成します"
    # ), inline=False)
    # embed2.add_field(name="Role setup Command", value=(
    #     "`role/create` リアクションをつけるとロール付与されるメッセージを作成します。"
    # ), inline=False)
    # embed2.add_field(name="Setting Command", value=(
    #     "`set/creater_role` クリエイターロールを設定します。設定することにより、クリエイターしかコマンドを実行できなくなります。\n"
    #     "`set/vc_categories <カテゴリ名>` VCを作成するカテゴリを指定します。\n"
    #     "`set/req_categories <カテゴリ名>` リクエストを作成するカテゴリを指定します。\n"
    #     "`set/req_ad_categories <カテゴリ名>` リクエスト(admin)を作成するカテゴリを指定します。\n"
    #     "`set/thread_categories <カテゴリ名>` スレッドを作成するカテゴリを指定します。\n"
    #     "`set/thread_name <スレッド名>` スレッドの名前を指定します。\n"
    # ), inline=False)
    # embed2.add_field(name="Request Manege Command", value=(
    #     "`req/create <title>` 新規リクエストを作成します。\n"
    #     "`req/close` リクエストを終了します。\n"
    # ), inline=False)
    # embed2.add_field(name="Admin Command", value=(
    #     "`admin/msg_create` Server Managerが参加している全てのギルドへメッセージを一斉送信します。\n"
    #     "`admin/show_groups` 変数'groups'を表示します。\n"
    #     "`admin/logs` 直近のlogs10行とlogsファイルを表示します。"
    # ), inline=False)
    # embed2.add_field(name="Thread Command", value=(
    #     "`th/create` スレッドを新たに作成します。\n"
    #     "`th/close` 変数'groups'を表示します。\n"
    # ), inline=False)
    # # embed2.add_field(name="Youtube&Twitter Command", value=(
    # #     "`youtube/set <YoutubeのチャンネルのURL>` チャンネルにアップロードをした際に、通知をします。\n"
    # #     "`twitter/set <TwitterのID>` Tweetをした際に、通知をします。\n"
    # #     "`youtube/remove <YoutubeのチャンネルのURL>` チャンネルを通知リストから削除します。\n"
    # #     "`twitter/remove <TwitterのID>` アカウントを通知リストから削除します。\n"
    # #     # "`mng/bans` Show listed bans."
    # # ), inline=False)
    # embed2.add_field(name="Help Center",
    #                  value=())
    # #   embed.add_field(name="System Command ( Only use cronちゃん )",value=(
    # #     "`sys/save`\n"
    # #     "`sys/load`"
    # #     ),inline=False)