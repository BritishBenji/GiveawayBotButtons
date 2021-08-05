import asyncio
import datetime
import json
import os
import time

import discord
import discord_slash
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components

with open('./config.json', 'r') as cjson:
    config = json.load(cjson)

guilds = []


def get_prefix(client, message):
    # sets the prefixes, you can keep it as an array of only 1 item if you need only one prefix
    prefixes = [config["prefix"]]

    if not message.guild:
        # Only allow '*' as a prefix when in DMs, this is optional
        prefixes = [config["prefix"]]

    return commands.when_mentioned_or(*prefixes)(client, message)


bot = commands.Bot(command_prefix=get_prefix, description="A simple giveaway bot",
                   case_insensitive=True)
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)


@bot.event
# connects to discord
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    while len(guilds) < 1:
        async for guild in bot.fetch_guilds(limit=150):
            guilds.append(guild.name)
    print(guilds)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(f'cogs.{filename}')

bot.run(config["token"], bot=True, reconnect=True)
