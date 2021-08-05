import asyncio
import datetime
import json
import os
import time
import random

import discord
import discord_slash
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components
from main import get_prefix


class GiveawayTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = json.load(open("config.json", "r"))
        self.color = discord.Colour.blurple()
        self.giveaway_task.start()

    def cog_unload(self):
        self.giveaway_task.cancel()

    @tasks.loop(seconds=5)
    async def giveaway_task(self):
        await self.bot.wait_until_ready()
        users = []
        with open("cogs/giveaways.json", "r") as f:
            giveaways = json.load(f)

        if len(giveaways) == 0:
            return

        for giveaway in giveaways:
            data = giveaways[giveaway]
            if int(time.time()) > data["end_time"]:
                channel = self.bot.get_channel(data["channel_id"])
                giveaway_message = await channel.fetch_message(int(giveaway))
                with open(f"giveaway_users/{data['button_id']}.txt", "r") as file:
                    for line in file:
                        stripped_line = line.strip()
                        users.append(stripped_line)

                if len(users) < data["winners"]:
                    winners_number = len(users)
                else:
                    winners_number = data["winners"]

                winners = random.sample(users, winners_number)
                users_mention = []
                result_embed = discord.Embed(
                    title="🎉 {} 🎉".format(data["prize"]),
                    color=self.color,
                    description="Congratulations to the winners!"
                )
                for user in winners:
                    result_embed.add_field(name="Winner:", value=f"<@{user}>", inline=True)
                result_embed.set_footer(icon_url=self.bot.user.avatar_url, text="Giveaway Ended !")
                result_embed.set_thumbnail(url=self.bot.user.avatar_url)

                await giveaway_message.edit(embed=result_embed, components=[])

                with open("cogs/giveaways.json", "r") as file:
                    json_data = json.load(file)

                    del json_data[giveaway]
                if os.path.exists(f"giveaway_users/{data['button_id']}.txt"):
                    os.remove(f"giveaway_users/{data['button_id']}.txt")
                else:
                    pass

                with open("cogs/giveaways.json", "w") as file:
                    json.dump(json_data, file, indent=4)


def setup(bot):
    bot.add_cog(GiveawayTask(bot))
