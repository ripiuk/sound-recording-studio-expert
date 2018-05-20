import json
import logging

import requests


class ExpertBotHandler:

    def __init__(self, token: str):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.log = logging.getLogger(f'Bot.{type(self).__name__}')

    def get_updates(self, offset: int=None, timeout: int=30) -> list:
        """Make a GET request to get all the updates

        :param offset: Identifier of the first update to be returned.
        Must be greater by one than the highest among the identifiers of previously received updates.
        By default, updates starting with the earliest unconfirmed update are returned.
        :param timeout: Timeout in seconds for long polling. Defaults to 0, i.e. usual short polling.
        Should be positive, short polling should be used for testing purposes only.
        :return: a list of update results
        """
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result = resp.json()['result']
        self.log.debug(f'Got updates: {result}')
        return result

    def send_message(self, chat_id: int or str, text: str,
                     reply_markup: str=None, parse_mode: str='Markdown') -> requests.models.Response():
        """
        :param chat_id: Unique identifier for the target chat or username of the target channel
        :param text: Text of the message to be sent
        :param reply_markup: Additional interface options. A JSON-serialized object for an inline keyboard,
        custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
        :param parse_mode: Send Markdown or HTML, if you want Telegram apps to show bold, italic,
        fixed-width text or inline URLs in your bot's message.
        """
        method = 'sendMessage'
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        if reply_markup:
            params = {**params, 'reply_markup': reply_markup}
        resp = requests.post(self.api_url + method, params)
        self.log.debug(f'Message delivery status: {resp.status_code}')
        return resp

    def send_photo(self, chat_id: int or str, file_id: str, caption: str=None) -> requests.models.Response():
        """
        :param chat_id: Unique identifier for the target chat or username of the target channel
        :param file_id: Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers
        :param caption: Photo caption 0-200 characters
        """
        method = 'sendPhoto'
        params = {'chat_id': chat_id, 'photo': file_id}
        if caption:
            params = {**params, 'caption': caption}
        resp = requests.post(self.api_url + method, params)
        self.log.debug(f'Message delivery status: {resp.status_code}')
        return resp

    def get_last_update(self) -> tuple:
        """Get last update and parse a response

        :return: tuple(last_update_id, last_chat_text, last_chat_id)
        """
        get_result = self.get_updates()
        if not get_result:
            return None, None, None
        last_update = get_result[-1]
        return self.parse_update_message(last_update)

    @staticmethod
    def build_keyboard(items: list) -> str:
        """
        :param items: a list of button names
        :return: a JSON-serialized object for a custom reply keyboard
        """
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}
        return json.dumps(reply_markup)

    @staticmethod
    def remove_keyboards() -> str:
        reply_markup = {"remove_keyboard": True}
        return json.dumps(reply_markup)

    @staticmethod
    def parse_update_message(message: dict) -> tuple:
        last_update_id = message['update_id']
        # FIXME: if there will be no 'text' field?
        last_chat_text = message['message'].get('text')
        last_chat_id = message['message']['chat']['id']
        return last_update_id, last_chat_text, last_chat_id
