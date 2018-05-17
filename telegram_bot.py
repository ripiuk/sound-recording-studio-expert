import datetime

import requests

import misc


class ExpertBotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()
        last_update = get_result[-1] if len(get_result) > 0 else get_result[len(get_result)]
        return last_update


def main():
    my_token = misc.token
    expert_bot = ExpertBotHandler(my_token)
    new_offset = None

    while True:
        expert_bot.get_updates(new_offset)

        last_update = expert_bot.get_last_update()

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        if last_chat_text == '/lol':
            expert_bot.send_message(last_chat_id, 'LOOOOOOOL, {}'.format(last_chat_name))

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
