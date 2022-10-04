# This file contains almost everything of Engine Bot for Discord
import base64
import discord
import requests
from config import *
import logging

styles = ['SMB1', 'SMB3', 'SMW', 'NSMBU']


async def command_help(message: discord.Message):
    retval = '''📑 Commands available:
`e!help` : Check out this help.
`e!register` : Register user.
`e!query` : Query level.
`e!stats` : Publication statistics.'''
    if message.author.id in BOT_ADMIN:
        retval += '''
📑 Administrator commands available:
`e!permission` : Update permission.'''
    if message.author.get_role(GAME_ADMIN_ROLE):
        retval += '''
📑 Moderator commands available:
`e!ban` : Ban user.'''
    retval_es = '''📑 Comandos disponibles:
`e!help` : Mira esta ayuda.
`e!registrar` : Registrar usuario.
`e!consulta` : Consultar un nivel.
`e!estats` : Estadísticas de publicación.'''
    if message.author.id in BOT_ADMIN:
        retval_es += '''
📑 Comandos de administrador disponibles:
`e!permiso` : Permiso de actualización.'''
    if message.author.get_role(GAME_ADMIN_ROLE):
        retval_es += '''
📑 Comandos de moderador disponibles:
`e!prohibir` : Prohibir usuario.'''
    await message.reply(retval + '\n\n' + retval_es)
    return


async def command_register(message: discord.Message, locale):
    if message.content.strip() == locale.REGISTER_COMMAND:
        await message.reply(locale.REGISTER_HINT)
        return
    else:
        try:
            if ' ' not in message.content:
                await message.reply(locale.COMMAND_NO_SPACE)
                await message.reply(locale.REGISTER_HINT)
                await message.delete()
                return
            raw_register_code = message.content.split(' ')[1].strip()
            register_code = base64.b64decode(raw_register_code.strip().encode()).decode().split("\n")
            username = register_code[0]
            password_hash = register_code[1]
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/register',
                                          json={'username': username, 'password_hash': password_hash,
                                                'user_id': str(message.author.id),
                                                'api_key': ENGINE_TRIBE_API_KEY}).json()
            if 'success' in response_json:
                await message.reply(locale.REGISTER_SUCCESS + ' `' + str(response_json['username']) + '`.')
                await message.delete()
                return
            else:
                if response_json['error_type'] == '035':
                    await message.reply(
                        locale.REGISTER_FAILED + '\n' + locale.REGISTER_ONLY_ONE_USER + '\n' + message.author.name +
                        locale.REGISTER_ONLY_ONE_USER_2)  # 1 user id -> only one user
                    await message.delete()
                    return
                elif response_json['error_type'] == '036':
                    await message.reply(
                        locale.REGISTER_FAILED + '\n' +
                        response_json['username'] + locale.REGISTER_USER_ALREADY_EXISTS)  # username already exists
                    await message.delete()
                    return
                else:
                    await message.reply(
                        locale.REGISTER_FAILED + locale.UNKNOWN_ERROR + '\n' + response_json['error_type'] + '\n' +
                        response_json['message'])
                    await message.delete()
                    return
        except Exception as e:
            await message.reply(locale.REGISTER_FAILED + '\n' + locale.REGISTER_INVALID_CODE + str(e))  # Unknown error
            await message.delete()
            return


async def command_ban(message: discord.Message, locale):
    if not message.author.get_role(GAME_ADMIN_ROLE):
        await message.reply(locale.PERMISSION_DENIED)
        return
    if message.content.strip() == locale.BAN_COMMAND:
        await message.reply(locale.BAN_HINT)
        return
    else:
        try:
            username = message.content.split(' ')[1]
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/update_permission',
                                          json={'username': username, 'permission': 'banned',
                                                'value': True, 'api_key': ENGINE_TRIBE_API_KEY}).json()
            if 'success' in response_json:
                await message.reply('✅ ' + username + locale.BAN_SUCCESS)
                return
            else:
                await message.reply(locale.PERMISSION_UPDATE_FAILED + '\n' + str(response_json))
                return
        except Exception as e:
            await message.reply(locale.UNKNOWN_ERROR + '\n' + str(e))
            return


async def command_permission(message: discord.Message, locale):
    if message.author.id not in BOT_ADMIN:
        await message.reply(locale.PERMISSION_DENIED)
        return
    if message.content.strip() == locale.PERMISSION_COMMAND:
        await message.reply(locale.PERMISSION_HINT)
        return
    else:
        try:
            args = message.content.replace(message.content.split(' ')[0], '').strip().split(' ')
            username = args[0]
            permission = args[1]
            if str(args[2]).lower() == 'true':
                value = True
            else:
                value = False
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/update_permission',
                                          json={'username': username, 'permission': permission,
                                                'value': value, 'api_key': ENGINE_TRIBE_API_KEY}).json()
            if 'success' in response_json:
                await message.reply(
                    '✅ Updated ' + username + ' \'s ' + permission + ' to ' + str(value) + '.')
            else:
                await message.reply(locale.PERMISSION_UPDATE_FAILED + '\n' + str(response_json))
                return
        except Exception as e:
            await message.reply(locale.UNKNOWN_ERROR + '\n' + str(e))
            return


async def command_query(message: discord.Message, locale):
    if message.content.strip() == locale.QUERY_COMMAND:
        await message.reply(locale.QUERY_HINT)
        return
    else:
        level_id = message.content.split(' ')[1].upper()
        if '-' not in level_id:
            level_id = prettify_level_id(level_id)
        if len(level_id) != 19:
            await message.reply(locale.QUERY_INVALID_ID)
            return
        try:
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/stage/' + level_id,
                                          data='auth_code=' + locale.BOT_AUTH_CODE,
                                          headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
            if 'error_type' in response_json:
                await message.reply(locale.QUERY_NOT_FOUND)
                return
            else:
                level_data = response_json['result']
                retval = '🔍 ' + locale.QUERY_LEVEL + ': **' + level_data['name'] + '**\n'
                retval += 'Author: ' + level_data['author']
                if int(level_data['featured']) == 1:
                    retval += locale.QUERY_FEATURED
                retval += '\n'
                retval += '⏰ ' + level_data['date']
                retval += '  ' + str(level_data['likes']) + '❤ ' + str(level_data['dislikes']) + '💙\n'
                clears = level_data['victorias']
                plays = level_data['intentos']
                deaths = level_data['muertes']
                if int(plays) == 0:
                    retval += str(clears) + locale.QUERY_CLEARS + '/' + str(plays) + locale.QUERY_PLAYS + '\n'
                else:
                    retval += str(clears) + locale.QUERY_CLEARS + '/' + str(plays) + locale.QUERY_PLAYS + ' ' + str(
                        round((int(clears) / int(deaths)) * 100, 2)) + '%\n'
                retval += locale.QUERY_TAGS + level_data['etiquetas'] + locale.QUERY_STYLE + styles[
                    int(level_data['apariencia'])]
                await message.reply(retval)
                return
        except Exception as e:
            await message.reply(locale.UNKNOWN_ERROR + str(e))
            return


async def command_stats(message: discord.Message, locale):
    try:
        response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/info',
                                      json={'user_id': str(message.author.id)}).json()
        if 'error_type' in response_json:
            await message.reply(locale.STATS_NOT_FOUND)
            return
        else:
            user_data = response_json['result']
            retval = locale.STATS_TITLE + user_data['username'] + '\n'
            retval += locale.STATS_COUNT + str(user_data['uploads'])
            if str(user_data['uploads']) == '0':
                await message.reply(retval)
                return
            else:
                all_likes = 0
                all_dislikes = 0
                all_plays = 0
                retval += '\n'
                levels_data = requests.post(url=ENGINE_TRIBE_HOST + '/stages/detailed_search',
                                            data={'auth_code': locale.BOT_AUTH_CODE, 'author': user_data['username']},
                                            headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
                for level_data in levels_data['result']:
                    retval += '- ' + level_data['name'] + ' ' + str(level_data['likes']) + '❤ ' + str(
                        level_data['dislikes']) + '💙\n  ' + level_data['id']
                    if int(level_data['featured']) == 1:
                        retval += locale.QUERY_FEATURED
                    retval += '\n'
                    all_likes += int(level_data['likes'])
                    all_dislikes += int(level_data['dislikes'])
                    all_plays += int(level_data['intentos'])
                    retval += '  ' + locale.QUERY_TAGS + level_data['etiquetas'] + '\n'
                retval += locale.STATS_TOTAL_LIKES + str(all_likes) + locale.STATS_TOTAL_DISLIKES + str(
                    all_dislikes) + locale.STATS_TOTAL_PLAYS + str(all_plays)
                await message.reply(retval)
                return
    except Exception as e:
        await message.reply(locale.UNKNOWN_ERROR + str(e))
        return


def prettify_level_id(level_id: str):
    return level_id[0:4] + '-' + level_id[4:8] + '-' + level_id[8:12] + '-' + level_id[12:16]
