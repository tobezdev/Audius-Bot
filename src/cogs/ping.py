import discord
from discord.ext import commands


class Ping(commands.Cog):
    """A simple ping command to check if the bot is responsive."""
    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot: discord.AutoShardedBot = bot

    @commands.slash_command(name="ping", description="Check the bot's responsiveness.")
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        """Responds with the bot's latency in ms. Not really supposed to be helpful, just a test of bot responsiveness."""
        latency_ms: float = self.bot.latency * 1000
        await ctx.respond(content=f"Latency: **`{latency_ms:.2f}`**ms.")
        return

def setup(bot: discord.AutoShardedBot) -> None:
    """Setup function to add the Ping cog to the bot."""
    bot.add_cog(cog=Ping(bot=bot))
