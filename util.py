import discord


def get_channel_from_name(guild, name):
    channels = {}
    for x in guild.channels:
        channels[x.name] = x
    if name in channels:
        return channels[name]
    else:
        return guild.system_channel


def get_category_from_name(guild, name):
    categories = {}
    for x in guild.categories:
        categories[x.name] = x
    if name in categories:
        return categories[name]
    else:
        return False


def get_announce_channel(guild):
    system_ch = guild.system_channel
    ch = get_channel_from_name(guild, "お知らせ")
    if system_ch != ch:
        return ch
    else:
        ch = get_channel_from_name(guild, "おしらせ")
        if system_ch != ch:
            return ch
        else:
            if guild.text_channels[0] is None:
                return guild.owner
            else:
                return ch


def get_sum_members(client):
    result = 0
    for x in client.guilds:
        try:
            members = int(len(x.members))
            print(x.name+": "+str(members)+"人")
            result += members
        except Exception as e:
            print("except!!")
    return result


async def reload_activity(client,logging):
    await client.change_presence(
        activity=discord.Game(str(len(client.guilds)) + "servers | " + str(get_sum_members(client)) + " members"))
    logging.info(str(len(client.guilds)) + "個のサーバで稼働中")
