import discord
import asyncio
import re
import os
import sys
from collections import deque
from datetime import datetime, timedelta

# Bot token and channel IDs
TOKEN = "0000000000" # Replace with bot token
LOG_CHANNEL_ID = 1321744941742952478  # Replace with your Discord channel ID for logs
COMMAND_CHANNEL_ID = 1321744941742952478  # Replace with your Discord channel ID for commands
CHAT_CHANNEL_ID = 1313976249793642527

# Server executable path
SERVER_EXECUTABLE = 

# Default reset schedule (in hours)
RESET_INTERVAL_HOURS = 12

# Initialize Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Server process holder
server_process = None

# Message queues for rate-limiting
log_message_queue = deque()
chat_message_queue = deque()

def is_server_running():
    """Check if the server process is running."""
    global server_process
    return server_process is not None and server_process.returncode is None

async def send_command_to_server(command):
    """Send a command to the server."""
    global server_process

    if is_server_running():
        try:
            server_process.stdin.write((command + "\n").encode("utf-8"))
            await server_process.stdin.drain()
        except Exception as e:
            print(f"ERROR: Failed to send command: {e}")
    else:
        print("ERROR: Server process not running.")

async def restart_server():
    """Restart the server with improved error handling."""
    global server_process

    if is_server_running():
        try:
            server_process.terminate()
            await server_process.wait()
            print("INFO: Server terminated.")
        except Exception as e:
            print(f"ERROR: Failed to terminate server process: {e}")

    server_process = None
    await asyncio.sleep(10)

    for attempt in range(3):
        print(f"INFO: Attempting to restart server (Attempt {attempt + 1}/3).")
        try:
            server_process = await asyncio.create_subprocess_exec(
                SERVER_EXECUTABLE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            print("INFO: Server restarted successfully.")

            asyncio.create_task(monitor_server_output(server_process.stdout, log_message_queue, LOG_CHANNEL_ID))
            asyncio.create_task(monitor_server_output(server_process.stderr, log_message_queue, LOG_CHANNEL_ID))

            return
        except Exception as e:
            print(f"ERROR: Failed to restart server: {e}")
        await asyncio.sleep(5)
    print("ERROR: Failed to restart server after 3 attempts.")

async def schedule_reset():
    """Schedule periodic resets."""
    while True:
        await asyncio.sleep(RESET_INTERVAL_HOURS * 3600)  # Convert hours to seconds
        print("INFO: Performing scheduled reset...")
        await restart_server()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    if not is_server_running():
        await restart_server()

    asyncio.create_task(send_queued_messages(log_message_queue, LOG_CHANNEL_ID))
    asyncio.create_task(send_queued_messages(chat_message_queue, CHAT_CHANNEL_ID))
    asyncio.create_task(schedule_reset())

@client.event
async def on_message(message):
    print(f"DEBUG: Received message: {message.content} in channel {message.channel.id}")

    if message.author == client.user:
        return

    if message.channel.id == COMMAND_CHANNEL_ID:
        if message.content.startswith("!send"):
            command = message.content[len("!send "):].strip()
            if command:
                await send_command_to_server(command)
                await message.channel.send(f"Command sent to server: {command}")
                try:
                    await message.add_reaction("✅")
                except discord.errors.NotFound:
                    pass
                except discord.errors.Forbidden:
                    pass

        elif message.content.startswith("!say"):
            say_message = message.content[len("!say "):].strip()
            if say_message:
                await send_command_to_server(f"say {say_message}")
                await message.channel.send(f"Message sent to server: {say_message}")
                try:
                    await message.add_reaction("✅")
                except discord.errors.NotFound:
                    pass
                except discord.errors.Forbidden:
                    pass

        elif message.content.startswith("!kick"):
            player_name = message.content[len("!kick "):].strip()
            if player_name:
                await send_command_to_server(f"kick {player_name}")
                await message.channel.send(f"Player kicked: {player_name}")
                try:
                    await message.add_reaction("✅")
                except discord.errors.NotFound:
                    pass
                except discord.errors.Forbidden:
                    pass

        elif message.content.startswith("!ban"):
            player_name = message.content[len("!ban "):].strip()
            if player_name:
                await send_command_to_server(f"ban {player_name}")
                await message.channel.send(f"Player banned: {player_name}")
                try:
                    await message.add_reaction("✅")
                except discord.errors.NotFound:
                    pass
                except discord.errors.Forbidden:
                    pass

        elif message.content.startswith("!refresh"):
            await message.channel.send("Refreshing bot state...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif message.content.startswith("!restart"):
            await message.channel.send("Restarting server...")
            await restart_server()
            await message.channel.send("Server restarted.")

        elif message.content.startswith("!users"):
            await send_command_to_server("users")
            await message.channel.send("Fetching player list...")

async def monitor_server_output(stream, queue, channel_id):
    """Monitor and process server output asynchronously."""
    while True:
        try:
            chunk = await stream.read(1024)
            if not chunk:
                if not is_server_running():
                    print("WARNING: Server process is no longer running.")
                break

            lines = chunk.decode(errors="ignore").strip().split("\n")
            for line in lines:
                line = line.strip()
                queue.append(line)

            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"ERROR: Failed to read server output: {e}")
            break

async def send_queued_messages(queue, channel_id):
    """Send messages from the queue to the specified channel."""
    channel = client.get_channel(channel_id)
    if not channel:
        print(f"ERROR: Channel with ID {channel_id} not found.")
        return

    while True:
        if queue:
            message = queue.popleft()
            try:
                await channel.send(message)
            except discord.errors.HTTPException as e:
                print(f"ERROR: Failed to send message: {e}")
        await asyncio.sleep(0.5)

client.run(TOKEN)
