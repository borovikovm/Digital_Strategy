import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os


load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))
url = 'https://ria.ru/'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(os.getenv('CREDENTIALS'), scope)
client = gspread.authorize(credentials)
SPREADSHEET_ID = 'SHEET_ID'


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📰 Собрать заголовки новостей')
    markup.add(btn1)
    bot.send_message(message.from_user.id, 'Привет! Я - бот собиратор заголовков с новостного сайта РИА новости.', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def collect_titles(message):
    if message.text == '📰 Собрать заголовки новостей':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.from_user.id, '🔎 Собираю заголовки...', reply_markup=markup)

        response = requests.get(url=url)
        soup = BeautifulSoup(response.text, 'lxml')
        data = soup.find_all('span', class_='cell-list__item-title')
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1

        for item in data:
            result = [str(datetime.datetime.now()), item.text]
            sheet.append_row(result)
        bot.send_message(message.from_user.id, 'Готово! Новости смотри здесь: https://docs.google.com/spreadsheets/d/1QhHVnwCQSjn1agZzJHqHg0YgXjU5urMyT3xms_ygCTU/edit#gid=0', reply_markup=markup)


bot.polling(none_stop=True, interval=0)
