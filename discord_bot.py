import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import io
import os
from dotenv import load_dotenv
from format_data import format_data

# Load environment variables from .env file
load_dotenv()

# Replace hardcoded token with environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_OBJ = discord.Object(id=750351983700869221)
STAFF_IDS = [733731050336944130,763408346581303327,742062538375561327,645670740875542540]
CHANNELS = {
    "single-print-auction": 1288166824571306056,
    "low-print-auction": 1288166867097354282,
    "event-auction": 1288167157368094820,
}
THREAD_PREFIX = {
    "single-print-auction": "SP",
    "low-print-auction": "LP",
    "event-auction": "Event",
}

# Initialize the bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

# Maintain thread counters
daily_thread_count = defaultdict(
    lambda: defaultdict(int))  # {date: {channel_name: count}}

SCAN_WINDOW = timedelta(days=2)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    synced = await bot.tree.sync(guild=GUILD_OBJ)
    print(f"Synced {len(synced)} commands to guild {GUILD_OBJ.id}")
    # await check_auction_channels()
    # print("Processing complete. Shutting down...")
    # await bot.close()  # Log out and terminate the bot

def is_staff(interaction: discord.Interaction):
    return interaction.user.id in STAFF_IDS

@bot.tree.command(name="createthreads", description="Create the auction threads.", guild=GUILD_OBJ)
@app_commands.check(is_staff)
async def check_auction_channels(interaction: discord.Interaction):
    await interaction.response.send_message("Creating the auction threads.", ephemeral=True)
    today = datetime.now().strftime("%m/%d/%Y")
    messages_date = datetime.now() - SCAN_WINDOW
    for channel_name, channel_id in CHANNELS.items():
        channel = bot.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_name} not found.")
            continue

        async for message in channel.history(limit=100, after=messages_date):  # Adjust the message limit as needed
            if message.author.bot:  # Ignore bot messages
                continue
            if message.flags.has_thread:  # Skip if a thread already exists
                # print(f"{channel_name}: Thread already exists for message {message.id}") # For debugging
                continue

            print(f"{channel_name}: Creating thread for message {message.id}") # For debugging
            # Increment the thread counter
            daily_thread_count[today][channel_name] += 1
            thread_number = daily_thread_count[today][channel_name]

            # Generate thread name
            auction_type = THREAD_PREFIX[channel_name]
            thread_name = f"{auction_type} Auction-{thread_number} | {today}"

            # Create the thread
            thread = await message.create_thread(name=thread_name)
            await thread.send(
                "-# Bids for the listing will go in this thread <@792827809797898240> <@204255221017214977> <@155149108183695360>"
            )

        await asyncio.sleep(3) # Add a delay between channel checks

@bot.tree.command(name="close", description="Lock and archive the current auction thread.", guild=GUILD_OBJ)
@app_commands.check(is_staff)
async def close(interaction: discord.Interaction):
    # Check if the command is used inside a thread
    if isinstance(interaction.channel, discord.Thread):
        await interaction.response.send_message("Closing this thread.", ephemeral=True)
        await interaction.channel.edit(locked=True, archived=True)
    else:
        await interaction.response.send_message("This command can only be used inside a thread.", ephemeral=True)

@bot.tree.command(name="formatdata", description="Format an exported listing file for posting.", guild=GUILD_OBJ)
@app_commands.describe(attachment="The `.txt` file to format.")
@app_commands.check(is_staff)
async def format_data_command(interaction: discord.Interaction, attachment: discord.Attachment):
    if not attachment.filename.endswith('.txt'):
        await interaction.response.send_message("Only `.txt` files are supported.", ephemeral=True)
        return

    # Read the content of the file
    file_content = await attachment.read()
    input_data = file_content.decode('utf-8')

    # Format the input data
    formatted_output = format_data(input_data)

    # Create a file-like object for the output
    output_file = io.BytesIO(formatted_output.encode('utf-8'))
    output_file.name = "formatted_output.txt"

    # Send the output file
    await interaction.response.send_message("Here is the formatted output:", file=discord.File(output_file))

# Run the bot
bot.run(BOT_TOKEN)