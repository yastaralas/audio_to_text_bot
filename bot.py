import os
import telebot
import requests
import speech_recognition as sr
import subprocess
import datetime
from config import TELEGRAM_BOT_TOKEN

logfile = str(datetime.date.today()) + '.log' # формируем имя лог-файла
token = TELEGRAM_BOT_TOKEN
bot = telebot.TeleBot(token)

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Привет! Ты можешь отправить мне голосовое сообщение, а я преобразую его в текст.\n\nПока я воспринимаю только русский язык, но я обязательно научусь распознавать и другие :)')

@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
# Основная функция, принимает голосовуху от пользователя
    try:
        print("Started recognition...")
        # Ниже пытаемся вычленить имя файла, да и вообще берем данные с мессаги
        file_info = bot.get_file(message.voice.file_id)
        path = file_info.file_path # Вот тут-то и полный путь до файла (например: voice/file_2.oga)
        fname = os.path.basename(path) # Преобразуем путь в имя файла (например: file_2.oga)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path)) # Получаем и сохраняем присланную голосвуху
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content) # вот именно тут и сохраняется сама аудио-мессага
        process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])# здесь используется ffmpeg для конвертации .oga в .vaw
        result = audio_to_text(fname+'.wav') # Вызов функции для перевода аудио в текст
        bot.reply_to(message, "Короче, в голосовом сказано: «{}».".format(result)) # Отправляем пользователю, приславшему файл, текст
    except sr.UnknownValueError as e:
        # Ошибка возникает, если сообщение не удалось разобрать. В таком случае отсылается ответ пользователю и заносим запись в лог ошибок
        bot.send_message(message.from_user.id,  "Прошу прощения, но я ничего не поняла")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:
        # В случае возникновения любой другой ошибки, отправляется соответствующее сообщение пользователю и заносится запись в лог ошибок
        bot.send_message(message.from_user.id,  "Произошли технические шоколадки.")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) +':' + str(e) + '\n')
    finally:
        # удаляем временные файлы с аудио сообщением
        os.remove(fname+'.wav')
        os.remove(fname+'.oga')

def audio_to_text(dest_name: str):
# Функция для перевода аудио, в формате ".vaw" в текст
    r = sr.Recognizer()
    # тут мы читаем наш .vaw файл
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU") # используя возможности библиотеки распознаем текст, так же тут можно изменять язык распознавания
    return result

bot.polling(none_stop=True, interval=0)