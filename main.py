import telebot
from telebot import types
import quiz

import pandas as pd
from my_token import token

bot = telebot.TeleBot(token)

def write_word(new_word, new_pinyin, new_translation, user):
    new_term_line = f"{new_word};{new_pinyin};{new_translation};{user}"
    with open("./data/word_dict.csv", "r", encoding="utf-8") as f:
        existing_terms = [l.strip("\n") for l in f.readlines()]
        title = existing_terms[0]
        old_terms = existing_terms[1:]
    terms_sorted = old_terms + [new_term_line]
    terms_sorted.sort()
    new_terms = [title] + terms_sorted
    with open("./data/word_dict.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(new_terms))

def get_dict_stats(message):
    user_terms = 0
    db_terms = 0
    defin_len = []
    with open("./data/word_dict.csv", "r", encoding="utf-8") as f:
        for line in f.readlines()[1:]:
            word, pinyin, trans, added_by = line.split(";")
            # words = defin.split()
            # defin_len.append(len(words))
            if message.from_user.username in added_by:
                user_terms += 1
            else:
                db_terms += 1
    stats = {
        "terms_all": db_terms + user_terms,
        "terms_own": db_terms,
        "terms_added": user_terms,
        # "words_avg": sum(defin_len)/len(defin_len),
        # "words_max": max(defin_len),
        # "words_min": min(defin_len)
    }
    return stats


word_list = []
pinyin_list = []
translation_list = []

with open("./data/word_dict.csv", "r", encoding="utf-8") as f:
    existing_terms = [l.strip("\n") for l in f.readlines()]
    title = existing_terms[0]
    old_terms = existing_terms[1:]
    for term in old_terms:
        word, pinyin, trans, added_by = term.split(";")
        word_list.append(word)
        pinyin_list.append(pinyin)
        translation_list.append(trans)

print('words loaded')

word = ''
pinyin = ''
translation = ''

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Добавить слово')
    btn2 = types.KeyboardButton("Статистика")
    btn3 = types.KeyboardButton('Пройти тест')
    btn4 = types.KeyboardButton("Полезные ссылки")
    btn5 = types.KeyboardButton("Словарь")

    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, """\
Привет, {0.first_name}. Это бот для изучения китайского языка.\n
Что я умею:\n
/new_word - добавление нового слова\n
/stat - статистика слов в словаре\n
/dict - список слов в словаре\n
/start_quiz - квиз по словам\n
/links - полезные источники\n
Или же нажми на кнопки ниже:\n
""".format(message.from_user),
                     reply_markup=markup)

@bot.message_handler(commands=['dict'])
def show_words(message):
    words = ''
    print(word_list)
    for idx in range(len(word_list)):
        line = f'{idx+1}. {word_list[idx]} (_{pinyin_list[idx]}_) -  {translation_list[idx]}\n'
        words+=line
    bot.send_message(message.from_user.id, words, parse_mode="Markdown")

@bot.message_handler(commands=['commands'])
def send_commands(message):
    bot.send_message(message.from_user.id, """\
Что я умею:\n
/new_word - добавление нового слова\n
/stat - статистика слов в словаре\n
/start_quiz - квиз по словам\
""")

@bot.message_handler(content_types=['text'])
def some_commands(message):
    if message.text == '/new_word' or message.text == 'Добавить слово':
        bot.send_message(message.from_user.id, "Какое новое слово сегодня?")
        bot.register_next_step_handler(message, get_word)
    elif message.text == '/dict' or message.text == "Словарь":
        show_words(message)
    elif message.text == '/stat' or message.text == "Статистика":
        stat = get_dict_stats(message)
        terms_all = stat['terms_all']
        terms_added = stat['terms_added']
        bot.send_message(message.from_user.id, f'Всего слов в словаре: {terms_all} \nДобавлено {message.from_user.username}: {terms_added}')
    elif message.text == '/start_quiz' or message.text == 'Пройти тест':
        start_quiz(message)
    elif message.text == '/links' or message.text == "Полезные ссылки":
        links(message)
    else:
        send_commands(message)

def get_word(message):
    global word
    word = message.text
    bot.send_message(message.from_user.id, 'Введите пиньинь:')
    bot.register_next_step_handler(message, get_pinyin)

def get_pinyin(message):
    global pinyin
    pinyin = message.text
    bot.send_message(message.from_user.id, 'Какой перевод?')
    bot.register_next_step_handler(message, get_translation)

def get_translation(message):
    global translation
    translation = message.text
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = f'Новое слово {word} {pinyin}, что переводится как {translation}?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

# def get_age(message):
#     global age;
#     while age == 0: #проверяем что возраст изменился
#         try:
#              age = int(message.text) #проверяем, что возраст введен корректно
#         except Exception:
#              bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
#       bot.send_message(message.from_user.id, 'Тебе '+str(age)+' лет, тебя зовут '+name+' '+surname+'?')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        # код сохранения данных, или их обработки
        word_list.append(word)
        pinyin_list.append(pinyin)
        translation_list.append(translation)
        bot.send_message(call.message.chat.id, 'Запомню :)')
        write_word(word, pinyin, translation, call.message.chat.username)

    elif call.data == "no":
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Добавить слово')
        btn2 = types.KeyboardButton("Статистика")
        btn3 = types.KeyboardButton('Пройти тест')
        btn4 = types.KeyboardButton("Полезные ссылки")
        btn5 = types.KeyboardButton("Словарь")

        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(call.message.chat.id, 'Введем другое слово?', reply_markup=markup) #переспрашиваем


# @bot.message_handler(commands=['button'])
# def button_message(message):
#     markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1=types.KeyboardButton("Статистика")
#     item2=types.KeyboardButton("Словарь")
#     markup.add(item1)
#     markup.add(item2)
#     bot.send_message(message.chat.id,'Выберите, что вам надо',reply_markup=markup)

# @bot.message_handler(content_types='text')
# def message_reply(message):
#     if message.text=="Статистика":
#         stat = get_dict_stats()
#         terms_all = stat['terms_all']
#         terms_added = stat['terms_added']
#         bot.send_message(message.chat.id,
#                          f'Всего слов в словаре: {terms_all} \nДобавлено {message.from_user.username}: {terms_added}')
#     if message.text=="Словарь":
#         for i in range(len(word_list)):
#             words = f'{word_list[i]} ({pinyin_list[i]}) - {translation_list[i]}'
#         bot.send_message(message.from_user.id, text=words)

# bot.polling(none_stop=True, interval=0)

"""Глобальная переменная, в которой хранится словарь:
ключи -- ключи сессий, значения -- объекты Quiz."""
global quizzes

@bot.message_handler(commands=['start_quiz'])
def start_quiz(message):
    global quizzes
    if 'quizzes' in globals():
        quizzes[message.from_user.id] = quiz.Quiz()
    else:
        quizzes = dict()
        quizzes[message.from_user.id] = quiz.Quiz()

    term = quizzes[message.from_user.id].next_qna()[1]
    bot.send_message(message.chat.id, term)
    bot.register_next_step_handler(message, check_answer)


def check_answer(message):
    if 'quizzes' not in globals():
        bot.reply_to(message, 'Квиз не начат. Введите /start_quiz, чтобы начать квиз.')
    elif message.from_user.id not in quizzes:
        bot.reply_to(message, 'Квиз не начат. Введите /start_quiz, чтобы начать квиз.')
    else:
        try:
            term = quizzes[message.from_user.id].next_qna()[1]
            bot.send_message(message.chat.id, term)
            quizzes[message.from_user.id].record_user_answer(message.text)
            bot.register_next_step_handler(message, check_answer)
        except StopIteration:
            quizzes[message.from_user.id].record_user_answer(message.text)
            results = " ".join(quizzes[message.from_user.id].check_quiz())
            bot.send_message(message.chat.id, results)
            send_commands(message)

# bot.polling(none_stop=True)

keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False, one_time_keyboard=True)
stop = types.KeyboardButton(text='отмена ❌')
keyboard.add(stop)


@bot.message_handler(commands=['links']) #создаем команду
def links(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Сайт БКРС>", url='https://bkrs.info/')
    button2 = types.InlineKeyboardButton("Словарь LINE Dict>", url='https://dict.naver.com/linedict/zhendict/#/cnen/home')

    markup.add(button1)
    markup.add(button2)

    bot.send_message(message.chat.id, "Нажми на кнопку и перейди на сайт)".format(message.from_user), reply_markup=markup)

# bot.infinity_polling()
bot.polling(none_stop=True)