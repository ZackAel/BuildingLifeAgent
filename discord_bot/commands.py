import os
import datetime
import asyncio
import discord
from discord.ext import commands, tasks

from tasks import load_tasks, save_tasks, complete_task, record_task_date
from streak import get_current_streak
from mood import log_mood, get_today_mood


class ProductivityCog(commands.Cog):
    """Discord bot commands for productivity management."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_id = int(os.getenv("DISCORD_USER_ID", 0))
        self.friend_id = int(os.getenv("ACCOUNTABILITY_FRIEND_ID", 0))
        self.standup_time = datetime.time(hour=18, minute=0)
        self.standup_loop.start()

    def cog_unload(self) -> None:
        self.standup_loop.cancel()

    # --- Scheduled tasks -------------------------------------------------
    @tasks.loop(time=datetime.time(hour=18, minute=0))
    async def standup_loop(self) -> None:
        """Send daily standup question via DM."""
        if not self.user_id:
            return
        user = await self.bot.fetch_user(self.user_id)
        if user:
            await user.send("What did you accomplish today?")

    # --- Commands --------------------------------------------------------
    @commands.command(name="tasks")
    async def tasks_cmd(self, ctx: commands.Context) -> None:
        """List current tasks."""
        tasks_list = load_tasks()
        if not tasks_list:
            await ctx.send("No tasks found.")
            return
        msg = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks_list))
        await ctx.send(msg)

    @commands.command(name="addtask")
    async def add_task_cmd(self, ctx: commands.Context, *, task: str) -> None:
        """Add a new task."""
        tasks_list = load_tasks()
        tasks_list.append(task)
        save_tasks(tasks_list)
        record_task_date(task)
        await ctx.send(f"Added task: {task}")

    @commands.command(name="complete")
    async def complete_cmd(self, ctx: commands.Context, index: int) -> None:
        """Complete a task by index."""
        tasks_list = load_tasks()
        if 0 < index <= len(tasks_list):
            task = tasks_list.pop(index - 1)
            save_tasks(tasks_list)
            complete_task(task)
            await ctx.send(f"Completed: {task}")
        else:
            await ctx.send("Invalid task number.")

    @commands.command(name="streak")
    async def streak_cmd(self, ctx: commands.Context) -> None:
        """Share your current streak with an accountability buddy."""
        streak = get_current_streak()
        msg = f"My current streak is {streak} days!"
        await ctx.send(msg)
        if self.friend_id:
            friend = await self.bot.fetch_user(self.friend_id)
            if friend:
                await friend.send(msg)

    @commands.command(name="mood")
    async def mood_cmd(self, ctx: commands.Context, *, mood: str) -> None:
        """Log mood and react with an emoji."""
        log_mood(mood)
        emoji = "😊"
        if "tired" in mood.lower():
            emoji = "😴"
        elif "stressed" in mood.lower():
            emoji = "😰"
        await ctx.message.add_reaction(emoji)
        await ctx.send(f"Logged mood: {mood}")

    @commands.command(name="pomodoro")
    async def pomodoro_cmd(self, ctx: commands.Context, channel_id: int) -> None:
        """Join a voice channel and run a pomodoro timer."""
        channel = self.bot.get_channel(channel_id)
        if isinstance(channel, discord.VoiceChannel):
            vc = await channel.connect()
            await ctx.send("Pomodoro started for 25 minutes.")
            try:
                await asyncio.sleep(25 * 60)
            finally:
                await vc.disconnect()
                await ctx.send("Pomodoro finished. Take a break!")
        else:
            await ctx.send("Invalid voice channel id.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ProductivityCog(bot))
