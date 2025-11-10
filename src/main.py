import discord
from discord import errors
from discord.ext import commands

import os, dotenv
import string, random

from globals import COGS_PATH
from typing import Optional

from rich.theme import Theme
console_theme = Theme(
    styles={
        "info": "deep_sky_blue4",
        "debug": "deep_sky_blue4",
        "success": "bold bright_green",
        "warning": "bold yellow2",
        "error": "bold bright_red",
    }
)

from rich.console import Console
console = Console(
    color_system="auto",
    soft_wrap=False,
    theme=Theme(),
    width=480,
    height=100,
    log_time=True,
    log_time_format="%Y-%m-%d @ %H:%M:%S"
)


env_loaded: bool = dotenv.load_dotenv()
if not env_loaded:
    console.print("[WARNING/main]: .env file not found or failed to load. Proceeding with existing environment variables set by the system.")

# Default intents (everything except from privileged intents) 
i: discord.Intents = discord.Intents.default() 
# Enable message content for scanning (AutoMod) and maybe some prefix commands in the future.
i.message_content = True


bot: discord.AutoShardedBot = discord.AutoShardedBot(
    owner_ids=[
        969254887621820526, # tobezdev
        251252940004786180, # Michael
        555150451369181185  # SenjienZ
    ],    
    debug_guilds=[
        #
        # Uncomment these as added to prevent global command registration.
        # They are currently commented out to prevent a discord.errors.Forbidden exception
        # when trying to register commands in guilds it is not allowed to access (because it is not installed there).
        #
        # 557662127305785361, # Audius Community Guild ID
        # 871816769982058517, # Audius Community Staff Guild ID
        #
        1416809617488609545 # Toby's Tavern (Testing Guild) ID
    ],
    default_command_contexts={discord.InteractionContextType.guild},
    default_command_integration_types={discord.IntegrationType.guild_install},
    intents=i,
)


@bot.event
async def on_ready() -> None:
    if not bot.user:
        console.print("[ERROR/bot]: Bot failed to log in. Closing connection...")
        await bot.close()
        return
    else:
        console.print(f"[INFO/bot]: Logged in as {bot.user} (ID: {bot.user.id})")
        await bot.sync_commands(force=True, method="individual")
        console.print("[INFO/bot]: Synced commands with the Discord API.")
        return


# A generic error handler for all application commands. 
# Can be overridden with in-place try/except blocks in individual commands 
# or with cog-/command-specific error handlers using the on_command_error wrapper.
@bot.event 
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException) -> None:
    msg: Optional[str] = None
    errcode: str = ''.join(random.choices(population=string.ascii_uppercase+string.ascii_lowercase+string.digits, k=12))
    match error:
        case commands.CommandNotFound():
            msg = "That command doesn't exist."
        case commands.MissingRequiredArgument():
            msg = "You forgot to include a required argument."
        case commands.BadArgument():
            msg = "One or more arguments were invalid or in the wrong format."
        case commands.DisabledCommand():
            msg = "That command is currently disabled."
        case commands.NoPrivateMessage():
            msg = "This command can't be used in DMs."
        case commands.MissingPermissions():
            msg = "You don't have the required permissions to use this command."
        case commands.BotMissingPermissions():
            msg = "I don't have the required permissions to perform that action."
        case commands.CommandOnCooldown():
            msg = "That command is on cooldown. Try again in a moment."
        case commands.MaxConcurrencyReached():
            msg = "Too many people are using this command at once. Please try again later."
        case errors.ExtensionFailed():
            msg = "An extension failed to load due to an internal error."
        case errors.ExtensionNotFound():
            msg = "Couldn't find that extension."
        case errors.ExtensionAlreadyLoaded():
            msg = "That extension is already loaded."
        case errors.ExtensionNotLoaded():
            msg = "That extension isn't currently loaded."
        case commands.NotOwner():
            msg = "Only the bot owner can use this command."
        case commands.CheckFailure():
            msg = "You didn't pass a permission or condition check for this command."
        case commands.CommandInvokeError():
            msg = "An unexpected error occurred while running that command."
        case discord.InteractionResponded():
            msg = "This interaction has already been responded to."
        case discord.ApplicationCommandInvokeError():
            msg = "Something went wrong while executing that application command."
        case discord.CheckFailure():
            msg = "You don't meet the requirements to run this interaction."
        case discord.Forbidden():
            msg = "I don't have permission to do that."
        case discord.NotFound():
            msg = "That resource couldn't be found."
        case discord.DiscordServerError():
            msg = "Discord's servers had an internal error."
        case discord.HTTPException():
            msg = "A request to Discord's API failed unexpectedly."
        case discord.ConnectionClosed():
            msg = "The connection to Discord was unexpectedly closed."
        case discord.GatewayNotFound():
            msg = "Couldn't connect to Discord's gateway."
        case discord.InvalidArgument():
            msg = "One or more arguments provided were invalid."
        case discord.InvalidData():
            msg = "Discord returned invalid or incomplete data."
        case discord.ClientException():
            msg = "The bot encountered a misuse or internal setup issue."
        case discord.LoginFailure():
            msg = "The bot token provided is invalid."

    # Default error message for a non-specified exception type.
    if msg is None or msg == "":
        msg = f"An unknown error (`{error.__class__.__name__}`) occurred while processing this command."

    # Add an error code and contact email to each error in case further support is needed.
    msg += f"\nIf this error persists, please contact `toby@tobezdev.com`; quote error code **`{errcode}`** when reporting this issue."

    # Log the error with its code to the console for debugging purposes.
    console.print(f"[ERROR/command]: [{errcode}] Caught a {error.__class__.__name__} error in command '{ctx.command}'.\n\t\t{error}")
    await ctx.respond(msg, ephemeral=True)
    return


if __name__ == "__main__":
    token: Optional[str] = os.getenv(key="DISCORD_BOT_TOKEN")
    if token is None or token == "" or token.isspace():
        console.print("[ERROR/main]: No or empty token found in environment variables. Please set the 'DISCORD_BOT_TOKEN' variable.")
        exit(code=1)
    for filename in os.listdir(path=COGS_PATH):
        if filename.endswith(".py") and not filename == "__init__.py":
            try:
                _: list[str] = bot.load_extension(name=f"cogs.{filename[:-3]}")
                console.print(f"[INFO/bot]: Successfully loaded extension: '{filename}'.")
            except Exception as e:
                console.print(f"[ERROR/bot]: Failed to load extension '{filename}': {e}.")
    bot.run(token)

else:
    # Use regular print as the Console() won't exist for modular imports.
    try:
        print(f"[INFO/main]: Skipping execution of file '{os.path.realpath(path=__file__)}' due to modular import.")
    except Exception as e:
        print(f"[ERROR/main]: Error occurred while skipping file '{__file__}' due to modular import: {e.__class__.__name__}:\n\t{e}")
