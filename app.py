import discord
from config import *
from locales import EN, ES
from engine_bot import command_register, command_help, command_ban, command_query, command_stats, command_unban, \
    command_permission, command_random, command_server, command_error
# import logging

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or message.channel.id != COMMANDS_CHANNEL_ID:
        return
    if not message.content.startswith('e!'):  # command
        return
    elif message.content.startswith(EN.REGISTER_COMMAND):  # register EN
        await command_register(message=message, locale=EN)
    elif message.content.startswith(ES.REGISTER_COMMAND):  # register ES
        await command_register(message=message, locale=ES)
    elif message.content.startswith('e!help'):  # help command
        await command_help(message=message)
    elif message.content.startswith('e!ban'):  # ban EN
        await command_ban(message=message, locale=EN)
    elif message.content.startswith('e!prohibir'):  # ban ES
        await command_ban(message=message, locale=ES)
    elif message.content.startswith('e!unban'):  # unban EN
        await command_unban(message=message, locale=EN)
    elif message.content.startswith('e!desbanear'):  # unban ES
        await command_unban(message=message, locale=ES)
    elif message.content.startswith('e!query'):  # query EN
        await command_query(message=message, locale=EN)
    elif message.content.startswith('e!consulta'):  # query ES
        await command_query(message=message, locale=ES)
    elif message.content.startswith('e!stats'):  # stats EN
        await command_stats(message=message, locale=EN)
    elif message.content.startswith('e!estats'):  # stats ES
        await command_stats(message=message, locale=ES)
    elif message.content.startswith('e!permission'):  # permission EN
        await command_permission(message=message, locale=EN)
    elif message.content.startswith('e!permiso'):  # permission ES
        await command_permission(message=message, locale=ES)
    elif message.content.startswith('e!random'):  # random EN
        await command_random(message=message, locale=EN)
    elif message.content.startswith('e!azar'):  # random ES
        await command_random(message=message, locale=ES)
    elif message.content.startswith('e!server'):  # server stats
        await command_server(message=message)
    else:
        await command_error(message=message)
        return


client.run(BOT_TOKEN)
