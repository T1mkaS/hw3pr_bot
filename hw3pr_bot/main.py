import logging
import requests
import json
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
from config import token
import keyboards as kb
import random
from jokes import jokes
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


def get_news():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    url = 'https://www.securitylab.ru/news/'
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    cards = soup.find_all('a', class_='article-card')
    news = {}
    for card in cards:
        title = card.find('h2', class_='article-card-title').text.strip()
        description = card.find('p').text.strip()
        card_url = f'https://www.securitylab.ru{card.get("href")}'
        card_id = card_url.split('/')[-1]
        card_id = card_id[:-4]
        news[card_id] = {
            'card_url' : card_url,
            'title' : title,
            'description' : description
        }
    with open('news.json', 'w', encoding='utf-8') as file:
        json.dump(news, file, indent=4, ensure_ascii=False)

def news_update():
    with open('news.json', encoding='utf-8') as file:
        news_list = json.load(file)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    url = 'https://www.securitylab.ru/news/'
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    cards = soup.find_all('a', class_='article-card')

    fresh_news = {}

    for card in cards:
        card_url = f'https://www.securitylab.ru{card.get("href")}'
        card_id = card_url.split('/')[-1]
        card_id = card_id[:-4]
        if card_id in news_list:
            continue
        else:
            title = card.find('h2', class_='article-card-title').text.strip()
            description = card.find('p').text.strip()
            card_url = f'https://www.securitylab.ru{card.get("href")}'
            news_list[card_id] = {
                'card_url': card_url,
                'title': title,
                'description': description
            }
            fresh_news[card_id] = {
                'card_url': card_url,
                'title': title,
                'description': description
            }
    with open('news.json', 'w', encoding='utf-8') as file:
        json.dump(news_list, file, indent=4, ensure_ascii=False)
    return fresh_news


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.chat.id, f'Привет, {message.from_user.username}! Напиши /help и я расскажу, что умею!')

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await bot.send_message(message.chat.id, f'Напиши мне /start и я тебя поприветствую\nНапиши мне /news и погрузись в мир новостей!\nНапиши мне /buttons и я пошучу, а ты узнаешь про чат!\nНапиши /cancel и кнопки пропадут\nНапиши мне /help и узнай,что я могу')

@dp.message_handler(commands=['buttons'])
async def button(message: types.Message):
    await bot.send_message(message.chat.id, f'Поехали!',
                           reply_markup=kb.main_menu)

@dp.message_handler(commands=['news'])
async def news(message: types.Message):
    await bot.send_message(message.chat.id, 'Да начнется парсинг!', reply_markup=kb.start)

@dp.message_handler(commands=['cancel'])
async def news(message: types.Message):
    await bot.send_message(message.chat.id, 'Пока клавиатурам!', reply_markup=kb.empty)

@dp.message_handler(Text(equals='Все новости'))
async def news(message: types.Message):
    with open('news.json', encoding='utf-8') as file:
        news_dict = json.load(file)
    for k, v in news_dict.items():
        news = f'<b>{v["title"]}</b>\n{v["description"]}\n{v["card_url"]}'
        await message.answer(news)

@dp.message_handler(Text(equals='Последние 2 новости'))
async def two_news(message: types.Message):
    with open('news.json', encoding='utf-8') as file:
        news_dict = json.load(file)
    for k, v in list(news_dict.items())[-2:]:
        news = f'<b>{v["title"]}</b>\n{v["description"]}\n{v["card_url"]}'
        await message.answer(news)

@dp.message_handler(Text(equals='Свежие новости'))
async def fresh_news(message: types.Message):
    fresh = news_update()
    if len(fresh) > 0:
        for k, v in fresh.items():
            news = f'<b>{v["title"]}</b>\n{v["description"]}\n{v["card_url"]}'
            await message.answer(news)
    else:
        await message.answer('Свеженького пока нет! Ждем')


@dp.message_handler()
async def texts(message: types.Message):
    if message.text == 'Шутка':
        i = random.randint(0, len(jokes) - 1)
        await bot.send_message(message.chat.id, jokes[i])
    if message.text == 'Число участников в чате':
        try:
            await bot.send_message(message.chat.id, f'Нас в чате {await bot.get_chat_members_count(message.chat.id)}!')
        except Exception as ex:
            await bot.send_message(message.chat.id, "Что-то пошло не так")
    if message.text == 'Ссылка чата':
        try:
            chat = await bot.get_chat(message.chat.id)
            l = chat['invite_link']
            if l is not None:
                await bot.send_message(message.chat.id, f'Ссылка для приглашения: {l}!')
            else:
                await bot.send_message(message.chat.id, 'Мы не в чате! Ссылка доступна только для чатов')
        except Exception as ex:
            await bot.send_message(message.chat.id, "Что-то пошло не так")




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
