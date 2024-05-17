import os

from telebot import types
from dotenv import load_dotenv
from info import (
    help_message
)
from game import (
    Game,
    Player
)
import telebot

menu = {
  '/help': 'Помощь',
  '/start': 'Зарегистрироваться',
  '/play': 'Начать игру',
}
players = {}
games = {}

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)
menu_keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True,
                                          one_time_keyboard=True)
menu_keyboard.add(*menu.keys())
bot.set_my_commands(commands=[types.BotCommand(command, description) for command, description in menu.items()])


def answers_with_choice(options, one_time_keyboard=True):
    """Делает клавиатуру с вариантами ответа."""
    options = map(types.KeyboardButton, options)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                       one_time_keyboard=one_time_keyboard)
    markup.add(*options)
    return markup


class BotGame(Game):
    def __init__(self, player, json_file):
        super().__init__(player, json_file)
        self.output = lambda x: bot.send_message(
            player.id, self.process_output(x))

    def __str__(self):
        return f'Game={self.player}'

    def output_actions(self):
        """Выводит варианты действий."""
        location = self.player.location
        markup = answers_with_choice(location.available_actions.keys())
        bot.send_message(
            self.player.id, f"{self.process_output(location.description)}",
            reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, help_message)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name_user = message.from_user.first_name
    players[user_id] = Player(id=user_id, name=name_user)
    markup = answers_with_choice(['Мужской', 'Женский'])
    bot.send_message(user_id, f'''Привет, {name_user}! Добро пожаловать в игру.
                     Чтобы продолжить выбери пол''', reply_markup=markup)
    bot.register_next_step_handler(message, gender)


def gender(message):
    user_id = message.from_user.id
    players[user_id].set_gender(message.text)
    bot.send_message(user_id, 'Отлично, чтобы начать игру нажмите /play')


@bot.message_handler(commands=['play'])
def play(message):
    user_id = message.from_user.id
    if user_id not in players:
        bot.send_message(message.user_id, 'Вы не зарегистрированы')
        return
    games[user_id] = BotGame(player=players[user_id], json_file='location.json'
                             )
    games[user_id].player.location = games[user_id].locations['start']
    games[user_id].output_actions()


@bot.message_handler(func=lambda m: True)
def handler(message):
    choice = message.text
    user_id = message.from_user.id
    if choice not in games[user_id].player.location.available_actions.keys():
        bot.send_message(user_id, '''Можно выбрать только из вариантов,
                         предложенных в игре. Попробуй ещё раз!''')
    games[user_id].take_an_action(choice)
    if games[user_id].player.location.name_location != "exit":
        games[user_id].output_actions()
    else:
        bot.send_message(id, '''Игра окончена!''',
                         reply_markup=menu_keyboard)
        players[user_id].time_late = 0


bot.polling()
