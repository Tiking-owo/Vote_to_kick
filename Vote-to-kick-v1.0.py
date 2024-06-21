# 插件文件名: vote_to_kick.py

from mcdreforged.api.all import *
import time
import threading

PLUGIN_METADATA = {
    'id': 'vote_to_kick',
    'version': '1.0.0',
    'name': 'Vote to Kick',
    'description': 'A plugin to vote for kicking a player from the server',
    'author': 'Tiking_'
}

vote_data = {
    'initiator': None,
    'target': None,
    'yes_votes': 0,
    'no_votes': 0,
    'total_players': 0,
    'voting': False,
    'votes': {}
}

VOTING_DURATION = 60  # 投票持续时间（秒）

def start_vote(server: PluginServerInterface, initiator: str, target: str):
    global vote_data
    vote_data['initiator'] = initiator
    vote_data['target'] = target
    vote_data['yes_votes'] = 0
    vote_data['no_votes'] = 0
    vote_data['total_players'] = len(server.get_online_players())
    vote_data['voting'] = True
    vote_data['votes'] = {}

    server.say(f'{initiator} 发起投票，要将 {target} 踢出服务器，同意输入 !!yes，拒绝输入 !!no')

    def end_vote():
        time.sleep(VOTING_DURATION)
        if vote_data['voting']:
            conclude_vote(server)

    threading.Thread(target=end_vote).start()

def conclude_vote(server: PluginServerInterface):
    global vote_data
    vote_data['voting'] = False
    if vote_data['total_players'] > 0 and vote_data['yes_votes'] / vote_data['total_players'] > 0.8:
        server.execute(f'kick {vote_data["target"]}')
        server.say(f'{vote_data["target"]} 已被踢出服务器')
    else:
        server.say('投票玩家人数过低')
    vote_data['initiator'] = None
    vote_data['target'] = None
    vote_data['votes'] = {}

def on_load(server: PluginServerInterface, old_module):
    server.logger.info('Vote to Kick Plugin loaded')

def on_info(server: PluginServerInterface, info: Info):
    global vote_data
    if info.is_player:
        content = info.content
        if content.startswith('!!kick '):
            if vote_data['voting']:
                server.tell(info.player, '已有一个正在进行的投票，请稍后再试')
            else:
                target = content.split(' ')[1]
                start_vote(server, info.player, target)
        elif content == '!!yes':
            if vote_data['voting']:
                if info.player not in vote_data['votes']:
                    vote_data['yes_votes'] += 1
                    vote_data['votes'][info.player] = 'yes'
        elif content == '!!no':
            if vote_data['voting']:
                if info.player not in vote_data['votes']:
                    vote_data['no_votes'] += 1
                    vote_data['votes'][info.player] = 'no'

def on_unload(server: PluginServerInterface):
    server.logger.info('Vote to Kick Plugin unloaded')