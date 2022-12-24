from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Шутка")).add(KeyboardButton('Число участников в чате')).add(KeyboardButton('Ссылка чата'))
start = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Все новости')).add(KeyboardButton('Последние 2 новости')).add(KeyboardButton('Свежие новости'))

empty = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('ха-ха я не уйду'))