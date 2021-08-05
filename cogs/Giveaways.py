import asyncio
import datetime
import json
import os
import random
import time

import discord
import discord_slash
from discord import Member
from discord.ext import commands, tasks
from discord.ext.commands import MissingPermissions, has_permissions
from discord_slash import SlashCommand, SlashContext
from discord_slash.context import ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components
from main import get_prefix

giveaway_users = []


def convert(date):
    pos = ["s", "m", "h", "d"]
    time_dic = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}
    i = {"s": "Seconds", "m": "Minutes", "h": "Hours", "d": "Days"}
    unit = date[-1]
    if unit not in pos:
        return -1
    try:
        val = int(date[:-1])

    except ValueError:
        return -2

    if val == 1:
        return val * time_dic[unit], i[unit][:-1]
    else:
        return val * time_dic[unit], i[unit]


class Giveaways(commands.Cog):
    """
    This cog gives you control over the giveaways
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = json.load(open('./config.json', 'r'))
        self.color = discord.Colour.blurple()

    bot = commands.Bot(command_prefix=get_prefix, description="A bot made to describe the events in your server",
                       case_insensitive=True)
    slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

    @bot.command(name="Giveaway", description="Allows you to make a giveaway")
    @has_permissions(ban_members=True)
    async def Giveaways(self, ctx):
        """
        Use this commands to create a giveaway
        """
        await ctx.message.delete()
        init = await ctx.send(embed=discord.Embed(
            title="🎉 New Giveaway ! 🎉",
            description="Please answer the following questions to finalize the creation of the Giveaway",
            color=self.color)
                              .set_footer(icon_url=self.bot.user.avatar_url, text=self.bot.user.name))

        questions = [
            "What will the giveaway prize be?",
            "What Channel would you like the giveaway to be in? (Please mention the giveaway channel)",
            "How long will the giveaway run for? Example: (1d | 1h | 1m | 1s)",
            "How many winners do you want for this Giveaway?"
        ]

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        index = 1
        answers = []
        question_message = None
        for question in questions:
            embed = discord.Embed(
                title="Giveaway 🎉",
                description=question,
                color=self.color
            ).set_footer(icon_url=self.bot.user.avatar_url, text="Giveaway !")
            if index == 1:
                question_message = await ctx.send(embed=embed)
            else:
                await question_message.edit(embed=embed)

            try:
                user_response = await self.bot.wait_for("message", timeout=120, check=check)
                await user_response.delete()
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(
                    title="Error",
                    color=self.color,
                    description="You took too long to answer this question"
                ))
                return
            else:
                answers.append(user_response.content)
                index += 1
        try:
            channel_id = int(answers[1][2:-1])
        except ValueError:
            await ctx.send("You didn't mention the channel correctly, do it like {}.".format(ctx.channel.mention))
            return

        try:
            winners = abs(int(answers[3]))
            if winners == 0:
                await ctx.send("You did not enter an positive number.")
                return
        except ValueError:
            await ctx.send("You did not enter an integer.")
            return
        prize = answers[0].title()
        channel = self.bot.get_channel(channel_id)
        converted_time = convert(answers[2])
        if converted_time == -1:
            await ctx.send("You did not enter the correct unit of time (s|m|d|h)")
        elif converted_time == -2:
            await ctx.send("Your time value should be an integer.")
            return
        await init.delete()
        await question_message.delete()
        giveaway_embed = discord.Embed(
            title="🎉 {} 🎉".format(prize),
            color=self.color,
            description=f'» **{winners}** {"winner" if winners == 1 else "winners"}\n'
                        f'» Hosted by {ctx.author.mention}\n\n'
                        f'» **Click the button to join the giveaway!**\n'
        ) \
            .set_footer(icon_url=self.bot.user.avatar_url, text="Ends at") \
            .set_thumbnail(url=self.bot.user.avatar_url)

        giveaway_embed.timestamp = datetime.datetime.utcnow() + datetime.timedelta(seconds=converted_time[0])
        self.button_ID = str(random.randint(0, 1000))
        buttons = [
            manage_components.create_button(
                style=ButtonStyle.blue,
                label="Join Giveaway! 🎉",
                custom_id=self.button_ID
            ),
        ]
        action_row = manage_components.create_actionrow(*buttons)
        giveaway_message = await channel.send(embed=giveaway_embed, components=[action_row])
        now = int(time.time())
        with open("cogs/giveaways.json", "r") as f:
            giveaways = json.load(f)

            data = {
                "prize": prize,
                "host": ctx.author.id,
                "winners": winners,
                "end_time": now + converted_time[0],
                "channel_id": channel.id,
                "button_id": self.button_ID
            }
            giveaways[str(giveaway_message.id)] = data

        with open("cogs/giveaways.json", "w") as f:
            json.dump(giveaways, f, indent=4)
        with open(f"giveaway_users/{data['button_id']}.txt", "w"):
            pass

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        giveaway_users = []
        try:
            with open(f"giveaway_users/{ctx.custom_id}.txt", "r") as file:
                for line in file:
                    stripped_line = line.strip()
                    giveaway_users.append(stripped_line)

            if str(ctx.author.id) not in giveaway_users:
                await ctx.send("You have been entered into the giveaway!", hidden=True)
                a = ctx.author.id
                with open(f"giveaway_users/{ctx.custom_id}.txt", "a") as file:
                    file.write(f"{str(a)}\n")

            else:
                await ctx.send("You have already entered this giveaway!", hidden=True)
        except IOError:
            if len(str(ctx.custom_id)) <= 4:
                await ctx.send("This giveaway has ended!", hidden=True)


def setup(bot):
    bot.add_cog(Giveaways(bot))
