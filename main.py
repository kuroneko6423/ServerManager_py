import discord
from dotenv import load_dotenv
import os
import logger
import yaml

load_dotenv()
TOKEN = os.environ["TOKEN"]
client = discord.Client()

logging = logger.Logger('main')



@client.event
async def on_connect():
    logging.info("Connected to discord server.")


@client.event
async def on_ready():
    logging.info("Bot is ready.")


@client.event
async def on_message(msg):
    guild = msg.guild
    logging.info("GUILD_{0}({1})".format(guild.id, guild.name))
    logging.info("  NEW MESSAGE: {0}".format(msg.id))
    logging.info("    author: USER_{0}({1})".format(msg.author.id, msg.author.name))
    logging.info("    content: {0}".format(msg.content))

    try:
        if msg.content == "/help":
            pass
        op = msg.content.split('/', 1)[0]
        if op == "vc":
            pass
    except:
        pass


client.run(TOKEN)
