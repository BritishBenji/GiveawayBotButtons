import asyncio
import datetime
import os
import time

import discord
import discord_slash
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components
from config import TOKEN, PREFIX
guilds = []

bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), description="A simple giveaway bot",
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

bot.run(TOKEN, bot=True, reconnect=True)
