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
`e!register` : Register or change password.
`e!query` : Query level.
`e!random` : Random level.
`e!stats` : Publication statistics.
`e!server` : Server statistics.'''
    if message.author.id in BOT_ADMIN:
        retval += '''
📑 Administrator commands available:
`e!permission` : Update permission.'''
    if message.author.get_role(GAME_ADMIN_ROLE):
        retval += '''
📑 Moderator commands available:
`e!ban` : Ban user.
`e!unban` : Unban user.'''
    retval_es = '''📑 Comandos disponibles:
`e!help` : Mira esta ayuda.
`e!registrar` : Regístrese o cambie la contraseña.
`e!consulta` : Consultar un nivel.
`e!azar` : Nivel aleatorio.
`e!estats` : Estadísticas de publicación.
`e!server` : Estadísticas del servidor.'''
    if message.author.id in BOT_ADMIN:
        retval_es += '''
📑 Comandos de administrador disponibles:
`e!permiso` : Permiso de actualización.'''
    if message.author.get_role(GAME_ADMIN_ROLE):
        retval_es += '''
📑 Comandos de moderador disponibles:
`e!prohibir` : Prohibir usuario.
`e!desbanear` : Desbanear usuario.'''
    await message.reply(retval + '\n\n' + retval_es)
    return


async def command_register(message: discord.Message, locale):
    if message.content.strip() == locale.REGISTER_COMMAND:
        await message.reply(locale.REGISTER_HINT)
        return
    else:
        try:
            if ' ' not in message.content:
                await message.reply(f'{locale.COMMAND_NO_SPACE}\n{locale.REGISTER_HINT}')
                await message.delete()
                return
            raw_register_code = message.content.split(' ')[1].strip()
            register_code = base64.b64decode(raw_register_code.encode()).decode()\
                            .replace('\r\n','\n').replace('\r','\n').split("\n")
            operation = register_code[0]
            username = register_code[1]
            password_hash = register_code[2]
            if operation == 'r':  # register
                response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/register',
                                              json={'username': username, 'password_hash': password_hash,
                                                    'user_id': str(message.author.id),
                                                    'api_key': ENGINE_TRIBE_API_KEY}).json()
                if 'success' in response_json:
                    await message.reply(f'{locale.REGISTER_SUCCESS} `{str(response_json["username"])}` .')
                else:
                    if response_json['error_type'] == '035':
                        await message.reply(
                            f'{locale.REGISTER_FAILED}\n'
                            f'{locale.REGISTER_ONLY_ONE_USER}\n'
                            f'{response_json["username"]} {locale.REGISTER_ONLY_ONE_USER_2}')
                        # 1 user id -> only one user
                    elif response_json['error_type'] == '036':
                        await message.reply(
                            f'{locale.REGISTER_FAILED}\n'
                            f'`{response_json["username"]}` {locale.REGISTER_USER_ALREADY_EXISTS}')
                        # username already exists
                    else:
                        await message.reply(
                            f'{locale.REGISTER_FAILED}\n'
                            f'{locale.UNKNOWN_ERROR}\n'
                            f'{response_json["error_type"]} '
                            f'{response_json["message"]}')
                await message.delete()
                return
            elif operation == 'c':  # change password
                response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/update_password',
                                              json={'username': username, 'password_hash': password_hash,
                                                    'api_key': ENGINE_TRIBE_API_KEY}).json()
                if 'success' in response_json:
                    await message.reply(f'{locale.MODIFICATION_SUCCESS} `{str(response_json["username"])}` .')
                else:
                    await message.reply(f'{locale.MODIFICATION_FAILED} `{str(response_json["username"])}` .')
                await message.delete()
                return
            else:
                await message.reply(f'{locale.REGISTER_FAILED}\n'
                                    f'{locale.REGISTER_INVALID_CODE} (Invalid operation type)')
                await message.delete()
                return
        except Exception as e:
            await message.reply(f'{locale.REGISTER_FAILED}\n'
                                f'{locale.REGISTER_INVALID_CODE} (`{str(e)}`)')  # Unknown error
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


async def command_unban(message: discord.Message, locale):
    if not message.author.get_role(GAME_ADMIN_ROLE):
        await message.reply(locale.PERMISSION_DENIED)
        return
    if message.content.strip() == locale.UNBAN_COMMAND:
        await message.reply(locale.UNBAN_HINT)
        return
    else:
        try:
            username = message.content.split(' ')[1]
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/update_permission',
                                          json={'username': username, 'permission': 'banned',
                                                'value': False, 'api_key': ENGINE_TRIBE_API_KEY}).json()
            if 'success' in response_json:
                await message.reply('✅ ' + username + locale.UNBAN_SUCCESS)
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
                                          headers={'Content-Type': 'application/x-www-form-urlencoded',
                                                   'User-Agent': 'EngineBot/1'}).json()
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


async def command_random(message: discord.Message, locale):
    try:
        response_json = requests.post(url=ENGINE_TRIBE_HOST + '/stage/random',
                                      data='auth_code=' + locale.BOT_AUTH_CODE,
                                      headers={'Content-Type': 'application/x-www-form-urlencoded',
                                               'User-Agent': 'EngineBot/1'}).json()
        if 'error_type' in response_json:
            await message.reply(locale.QUERY_NOT_FOUND)
            return
        else:
            level_data = response_json['result']
            retval = '🔍 ' + locale.QUERY_LEVEL + ': **' + level_data['name'] + '**\n'
            retval += 'ID: `' + level_data['id'] + '`\n'
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
        if message.content == locale.STATS_COMMAND:
            request_body = {'user_id': str(message.author.id)}
        else:
            username = message.content.split(' ')[1].strip()
            request_body = {'username': username}
        response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/info',
                                      json=request_body).json()
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
                                            headers={'Content-Type': 'application/x-www-form-urlencoded',
                                                     'User-Agent': 'EngineBot/1'}).json()
                for level_data in levels_data['result']:
                    retval += '- ' + level_data['name'] + ' ' + str(level_data['likes']) + '❤ ' + str(
                        level_data['dislikes']) + '💙\n  ' + '`' + level_data['id'] + '`'
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


async def command_server(message: discord.Message):
    try:
        response_json = requests.get(url=ENGINE_TRIBE_HOST + '/server_stats').json()
        retval = '🗄️ **Server Statistics**\n'
        retval += f'🐧 OS: `{response_json["os"]}`\n'
        retval += f'🐍 Python Version: `{response_json["python"]}`\n'
        retval += f'👥 Player Count: `{response_json["player_count"]}`\n'
        retval += f'🌏 Level Count: `{response_json["level_count"]}`\n'
        retval += f'🕰️ Uptime: `{int(response_json["uptime"] / 60)}` minutes\n'
        retval += f'📊 Connection Per Minute: `{response_json["connection_per_minute"]}`'
        await message.reply(retval)
        return
    except Exception as e:
        await message.reply('Unknown error ' + str(e))
        return


async def command_error(message: discord.Message):
    await message.reply('❌ Comando incorrecto. ¡Por favor revise el mensaje anclado!')
    return


def prettify_level_id(level_id: str):
    return level_id[0:4] + '-' + level_id[4:8] + '-' + level_id[8:12] + '-' + level_id[12:16]
