import discord
from config import *
from locales import EN, ES
from engine_bot import command_register, command_help, command_ban, command_query, command_stats
from flask import Flask, request, jsonify
import threading

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

webhook_app = Flask('discord_bot_webhook')


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
    elif message.content.startswith('e!query'):  # query EN
        await command_query(message=message, locale=EN)
    elif message.content.startswith('e!consulta'):  # query ES
        await command_query(message=message, locale=ES)
    elif message.content.startswith('e!stats'):  # stats EN
        await command_stats(message=message, locale=EN)
    elif message.content.startswith('e!estats'):  # stats ES
        await command_stats(message=message, locale=ES)
    else:
        return


@webhook_app.route('/enginetribe', methods=['POST'])
async def webhook_enginetribe():
    webhook = request.get_json()
    if webhook['type'] == 'new_arrival':  # new arrival
        message = '📤 ' + webhook['author'] + ' subió un nuevo nivel: **' + webhook['level_name'] + '**\n'
        message += 'ID: ' + webhook['level_id']
        await client.get_channel(NOTIFICATIONS_CHANNEL_ID).send(message)
        return 'Success'
    if webhook['type'] == 'new_deleted':  # new deleted
        message = '🗑️ ' + webhook['author'] + ' borró el nivel:**' + webhook['level_name'] + '**'
        await client.get_channel(NOTIFICATIONS_CHANNEL_ID).send(message)
        return 'Success'
    if webhook['type'] == 'new_featured':  # new featured
        message = '🌟 El **' + webhook['level_name'] + '** de **' + webhook[
            'author'] + '** se ha agregado al nivel prometedor, ¡ven y juega!\n'
        message += 'ID: ' + webhook['level_id']
        await client.get_channel(NOTIFICATIONS_CHANNEL_ID).send(message)
        return 'Success'
    if 'likes' in webhook['type']:  # 10/100/1000 likes
        message = '🎉 Felicidades, el **' + webhook['level_name'] + '** de **' + webhook['author'] + '** tiene **' + \
                  webhook['type'].replace('_likes', '') + '** me gusta!\n'
        message += 'ID: ' + webhook['level_id']
        await client.get_channel(NOTIFICATIONS_CHANNEL_ID).send(message)
        return 'Success'
    if 'plays' in webhook['type']:  # 100/1000 plays
        message = '🎉 Felicidades, el **' + webhook['level_name'] + '** de **' + webhook[
            'author'] + '** ha sido reproducido **' +  webhook['type'].replace('_plays', '') + '** veces!\n'
        message += 'ID: ' + webhook['level_id']
        await client.get_channel(NOTIFICATIONS_CHANNEL_ID).send(message)
        return 'Success'
    if 'clears' in webhook['type']:  # 100/1000 clears
        message = '🎉 Felicidades, el **' + webhook['level_name'] + '** de **' + webhook[
            'author'] + '** ha salido victorioso **' +  webhook['type'].replace('_clears', '') + '** veces!\n'
        message += 'ID: ' + webhook['level_id']
        await client.get_channel(NOTIFICATIONS_CHANNEL_ID).send(message)
        return 'Success'
    return 'NotImplemented'


def run_webhook():
    webhook_app.run(host=WEBHOOK_HOST, port=WEBHOOK_PORT, debug=FLASK_DEBUG_MODE)


if __name__ == '__main__':
    threading.Thread(target=run_webhook, daemon=True).start()
    client.run(BOT_TOKEN)
