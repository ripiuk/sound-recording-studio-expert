import json

import requests

import misc
from experts.audio_interface_expert import AudioInterface


class ExpertBotHandler:

    def __init__(self, token: str):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

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
        return result

    def send_message(self, chat_id: int or str, text: str, reply_markup: str=None) -> requests.models.Response():
        """
        :param chat_id: Unique identifier for the target chat or username of the target channel
        :param text: Text of the message to be sent
        :param reply_markup: Additional interface options. A JSON-serialized object for an inline keyboard,
        custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
        """
        method = 'sendMessage'
        params = {'chat_id': chat_id, 'text': text}
        if reply_markup:
            params = {**params, 'reply_markup': reply_markup}
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self) -> tuple:
        """Get last update and parse a response

        :return: tuple(last_update_id, last_chat_text, last_chat_id)
        """
        get_result = self.get_updates()
        if not get_result:
            return None, None, None
        last_update = get_result[-1]
        return self._parse_update_message(last_update)

    @staticmethod
    def build_keyboard(items: list) -> str:
        """
        :param items: a list of button names
        :return: a JSON-serialized object for a custom reply keyboard
        """
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True, "remove_keyboard": True}
        return json.dumps(reply_markup)

    @staticmethod
    def remove_keyboards() -> str:
        reply_markup = {"remove_keyboard": True}
        return json.dumps(reply_markup)

    @staticmethod
    def _parse_update_message(message: dict) -> tuple:
        last_update_id = message['update_id']
        last_chat_text = message['message']['text']
        last_chat_id = message['message']['chat']['id']
        return last_update_id, last_chat_text, last_chat_id


def main():
    my_token = misc.token
    expert_bot = ExpertBotHandler(my_token)
    equipments = {
        'Audio interface': AudioInterface,
        'Soundproofing': AudioInterface,
        'Microphone': AudioInterface,
        'Studio monitor': AudioInterface,
        'Mixing console': AudioInterface
    }
    list_of_answers = ['No', 'Probably no', 'Don\'t know', 'Probably', 'Yes']
    new_offset = None

    while True:
        expert_bot.get_updates(new_offset)
        last_update_id, last_chat_text, last_chat_id = expert_bot.get_last_update()
        if not last_update_id:
            # Update response is empty
            continue

        if last_chat_text == '/menu':
            keyboard = expert_bot.build_keyboard(list(equipments.keys()))
            expert_bot.send_message(last_chat_id, 'Choose a type of sound recording equipment', reply_markup=keyboard)

        elif last_chat_text == '/help':
            expert_bot.send_message(
                chat_id=last_chat_id, text='\n'.join(
                    ['MusicStudioExpertBot is a bot, that can help you to provide a home sound recording studio.',
                     'To choose a category from menu - use this command: /menu',
                     'Also, this bot supports the following commands: /start /help /settings',
                     '---------------------',
                     'MusicStudioExpertBot допоможе вам з укомплектуванням домашньої студії звукозапису. '
                     'Вам лише необхідно відповісти на поставленні питання.',
                     'Щоб обрати категорію введіть команду: /menu',
                     'Також данний бот підтримує наступні команди: /start /help /settings']),
                reply_markup=expert_bot.remove_keyboards())

        elif last_chat_text in equipments:
            chosen_class = equipments[last_chat_text]
            expert_system = chosen_class()
            number_of_questions = len(expert_system.questions)
            question_number = 0

            while question_number != number_of_questions:
                # Send a question
                keyboard = expert_bot.build_keyboard(list_of_answers)
                expert_bot.send_message(chat_id=last_chat_id, text=expert_system.questions[question_number],
                                        reply_markup=keyboard)

                # Waiting for some response from user
                new_offset = last_update_id + 1
                expert_bot.get_updates(new_offset)
                last_update_id, last_chat_text, last_chat_id = expert_bot.get_last_update()
                if not last_update_id:
                    # Update response is empty
                    continue

                if last_chat_text == list_of_answers[0]:
                    expert_system.handle_answer(question_number, 0)
                elif last_chat_text == list_of_answers[1]:
                    expert_system.handle_answer(question_number, 1)
                elif last_chat_text == list_of_answers[2]:
                    question_number += 1
                    continue
                elif last_chat_text == list_of_answers[3]:
                    expert_system.handle_answer(question_number, 3)
                elif last_chat_text == list_of_answers[4]:
                    expert_system.handle_answer(question_number, 4)
                elif last_chat_text == '/stop':
                    break

                if last_chat_text in list_of_answers:
                    question_number += 1

            result = expert_system.get_result()
            expert_bot.send_message(
                last_chat_id, f"Result:\nProducer: {result.get('producer')}\nModel: {result.get('model')}\n",
                reply_markup=expert_bot.remove_keyboards())

        new_offset = last_update_id + 1
        # TODO: add localization UA/US


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
