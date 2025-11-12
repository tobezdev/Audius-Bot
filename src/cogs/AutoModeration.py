import discord
from discord.ext import commands

import requests, re

from typing import Optional, Any


AUDIUS_GUILD_ID: int = 557662127305785361
AUDIUS_STAFF_GUILD_ID: int = 871816769982058517
AUTOMOD_CONFIG: dict[str, bool] = {
    "block_discord_invites": True,
    "block_unsafelisted_urls": True,
    "block_profanity": True,
    "block_staff_impersonation": True,
}

# AutoMod safelists
URL_SAFELIST: list[str] = []
INVITE_SAFELIST: list[str] = []

# Add custom entries to block here.
PROFANITY_LIST: list[str] = []

# Add a list of profane words from a (maintained!!) external source to prevent huge source code.
for keyword in requests.get(url='https://raw.githubusercontent.com/zautumnz/profane-words/refs/heads/master/words.json').json():
    PROFANITY_LIST.append(keyword.lower())


async def scan_message_content(message: discord.Message) -> tuple[bool, Optional[str]]:
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

    if AUTOMOD_CONFIG.get("block_profanity", True):
        content_lower: str = message.content.lower()
        profane_words_found: list[str] = []

        leet_map: dict[int, str] = str.maketrans({
            '@': 'a', '4': 'a', '3': 'e', '1': 'i', '!': 'i',
            '0': 'o', '5': 's', '$': 's', '7': 't', '+': 't',
            '*': '', '-': '', '_': '', '.': '', ',': '', ' ': ''
        })

        for word in PROFANITY_LIST:
            if re.search(pattern=rf'\b{re.escape(pattern=word)}\b', string=content_lower):
                profane_words_found.append(word)

        tokens: list[Any] = re.findall(pattern=r'[a-z0-9@!$*+\-_]+', string=content_lower)
        normalized_tokens: list[str] = []
        for t in tokens:
            nt = t.translate(leet_map)
            nt: str = re.sub(pattern=r'[^a-z]', repl='', string=nt)
            nt: str = re.sub(pattern=r'(.)\1+', repl=r'\1', string=nt)
            if nt:
                normalized_tokens.append(nt)

        for word in PROFANITY_LIST:
            if word in profane_words_found:
                continue
            if any(word in nt for nt in normalized_tokens):
                profane_words_found.append(word)
        
        if profane_words_found:
            return (True, f"Profane word(s) detected: {', '.join(profane_words_found)}")


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