import telebot

from config import TOKEN, WHITE_LIST
from core import get_product

bot = telebot.TeleBot(TOKEN)

def login(chat_id):
    if(chat_id in WHITE_LIST):
        return True
    else:
        return False


@bot.message_handler(commands = ['start'])
def send_welcome(message):
        if(login(message.chat.id)):
            bot.reply_to(message, f'hewwooooooo, отправь пожожта артикул с вб!!!!')
        else:
            bot.send_maessage(message.chat.id, 'naaaaaaaaawr')

@bot.message_handler(content_types = ['text'])
def analitycs(message):
    if not login(message.chat.id):
        bot.send_maessage(message.chat.id, 'доступа нет((((')
        return
    try:
        article = message.text.strip()
        info = get_product(article)
        bot.send_message(message.chat.id, info)
    except ValueError:
        bot.send_message(message.chat.id, "ошибка, введите артикул")

bot.polling()

