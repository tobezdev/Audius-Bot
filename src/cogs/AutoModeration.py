import discord
from discord.ext import commands

import requests, re

from typing import Optional


AUDIUS_GUILD_ID: int = 871816769982058517
AUTOMOD_CONFIG: dict[str, bool] = {
    "block_discord_invites": True,
    "block_unsafelisted_urls": True,
}

# AutoMod safelists
URL_SAFELIST: list[str] = []
INVITE_SAFELIST: list[str] = []

# Add custom entries to block here.
PROFANITY_LIST: list[str] = []

# Add a list of profane words from a (maintained!!) external source to prevent huge source code.
for keyword in requests.get(url='https://raw.githubusercontent.com/zautumnz/profane-words/refs/heads/master/words.json').json():
    PROFANITY_LIST.append(keyword.lower())


async def scan_message(message: discord.Message) -> tuple[bool, Optional[str]]:
    """
    Scans messages to detect violations of various custom AutoMod rules.
    
    Returns tuple[bool, Optional[str]]: 
    - the first element indicates if a violation was found (True if yes, else False),
    - the second element provides the reason for the violation if applicable, else None.
    """
    no_violation = (False, None)

    # A simple filter for unsafelisted Discord invite links.
    if AUTOMOD_CONFIG.get("block_discord_invites", True):
        matches: Optional[list[str]] = re.findall(pattern=r'(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?', string=message.content)
        if matches and any(link not in URL_SAFELIST for link in matches):
            return (True, f"Unsafelisted Discord invite link(s) detected: {', '.join(matches)}")

    # Add logic here.
    # In the meantime, return no_violation to prevent every message 
    # being flagged as a violation by default and therefore deleted.

    return no_violation


class AutoModeration(commands.Cog):
    def __init__(self, bot: discord.AutoShardedBot) -> None:
        super().__init__(bot)
        self.bot: discord.AutoShardedBot = bot

    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages where the author is a bot.
        if message.author.bot:
            return
        
        # Ignore messages with no parent guild, or a parent guild which is not
        # the Audius community server, because we dont care about those.
        if not message.guild or message.guild.id != AUDIUS_GUILD_ID:
            return
        
        # Scan the message and store the result.
        res: tuple[bool, Optional[str]] = await scan_message(message=message)
        violation: bool = res[0]
        reason: Optional[str] = res[1]

        # Return early if there is no violation
        if not violation:
            return

        # If there is a violation, handle it accordingly.
        # At the moment, we simply delete the message as a 
        # placeholder until some proper logic is implemented here.
        try:
            await message.delete(reason=f"AutoMod: {reason}")
        except Exception:
            pass


def setup(bot: discord.AutoShardedBot) -> None:
    bot.add_cog(cog=AutoModeration(bot=bot))