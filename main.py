import telebot
import csv
from telebot import types

with open('telegram_token.txt', 'r') as f:
    bot = telebot.TeleBot(f.read())
forms = {i: 'очка' for i in range(2, 5)}
for i in range(5, 9 + 1):
    forms[i] = 'очков'
forms[1] = 'очко'
forms[0] = 'очков'
delimeters = ['.', ',', '/', ':', '-']
score_biatl = 0
score_triatl = 0
score_tetratl_1 = score_tetratl_2 = 0
score_pentatl_1 = score_pentatl_2 = score_pentatl_3 = 0


def text_preprocessing(s: str):
    last_delimeter = ''
    for i in s:
        if i in delimeters and last_delimeter == '':
            last_delimeter = i
        elif (i in delimeters and i != last_delimeter) or i not in '.,/: -1234567890':
            return 0
    if not last_delimeter and ' ' in s:
        delimeters.append(' ')
    for i in delimeters:
        if i in s:
            if len(s.split(i)) <= 3:
                return s.split(i)
            else:
                return 0
    return 0


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        keyboard = types.InlineKeyboardMarkup()
        type_choice = types.InlineKeyboardButton(text='📋 выбор вида 📋', callback_data='choose')
        help_about = types.InlineKeyboardButton(text='📣 помощь 📣', callback_data='help')
        discipline_choice = types.InlineKeyboardButton(text='📑 выбор дисциплины 📑', callback_data='types')
        keyboard.add(discipline_choice)
        keyboard.add(type_choice)
        keyboard.add(help_about)
        bot.send_photo(message.from_user.id, photo=open('logo.png', 'rb'), caption='меню', reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, 'напиши /start')


def get_time_100(message):
    text = message.text
    if text_preprocessing(text):
        text = text_preprocessing(text)
    else:
        pass
    text = [int(i) for i in text]
    swim_menu_100m = types.InlineKeyboardMarkup()
    try_again_100m = types.InlineKeyboardButton(text='✍️ посчитать ещё раз ✍️', callback_data='100m')
    get_back_100_200m = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='swim')
    swim_menu_100m.add(try_again_100m)
    swim_menu_100m.add(get_back_100_200m)
    if len(text) == 3:
        if text[2] <= 50:
            score = (80 - text[0] * 60 - text[1]) * 4 + 250
        else:
            score = (80 - text[0] * 60 - text[1] - 1) * 4 + 252
    elif len(text) == 2 and text[0] > 40:
        if text[1] <= 50:
            score = (80 - text[0]) * 4 + 250
        else:
            score = (80 - text[0] - 1) * 4 + 252
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_100m)
        return 0
    bot.send_message(message.from_user.id, f'Это {score} {forms[score % 10]}\nстоимость секунды - 4', reply_markup=swim_menu_100m)


def get_time_200(message):
    text = message.text
    swim_menu_200m = types.InlineKeyboardMarkup()
    try_again_200m = types.InlineKeyboardButton(text='✍️ посчитать ещё раз ✍️', callback_data='200m')
    get_back_100_200m = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='swim')
    swim_menu_200m.add(try_again_200m)
    swim_menu_200m.add(get_back_100_200m)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 3:
            if text[2] <= 50:
                score = (238 - text[0] * 60 - text[1]) * 2 + 74
            else:
                score = (238 - text[0] * 60 - text[1] - 1) * 2 + 75
            bot.send_message(message.from_user.id, f'Это {score} {forms[score % 10]}\nстоимость секунды - 2', reply_markup=swim_menu_200m)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_200m)


def get_fence_score(message):
    fence_menu = types.InlineKeyboardMarkup()
    try_again_fence = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='fencing')
    get_back_fencing = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='choose')
    fence_menu.add(try_again_fence)
    fence_menu.add(get_back_fencing)
    text = message.text
    if len(text.split('/')) > 1 or len(text.split()) > 1:
        if text_preprocessing(text):
            wins, losses = map(int, text_preprocessing(text))
        else:
            wins = losses = 0
        matches = wins + losses
        score_of_250 = one_win_score = 0
        fence_scores = list(csv.reader(open('fence_scores.csv')))
        for i in range(len(fence_scores)):
            fence_scores[i] = [int(j) for j in fence_scores[i][0].split(';')]
            if fence_scores[i][1] == matches:
                one_win_score = fence_scores[i][2]
                score_of_250 = fence_scores[i][0]
        score = 250 - (score_of_250 - wins) * one_win_score
        if score_of_250 > 0:
            bot.send_message(message.from_user.id,
                             f'Это {score} {forms[score % 10]}\nСтоимость одного укола - {one_win_score}',
                             reply_markup=fence_menu)
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=fence_menu)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=fence_menu)


def biatl_run(message):
    text = message.text
    biatl_run_menu = types.InlineKeyboardMarkup()
    biatl_run_again = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='1000m')
    biatl_run_get_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='run')
    biatl_run_menu.add(biatl_run_again)
    biatl_run_menu.add(biatl_run_get_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 3:
            if text[2] == 0:
                score = (4 * 60 + 40 - text[0] * 60 - text[1]) * 2 + 171
            elif text[2] <= 50:
                score = (4 * 60 + 40 - text[0] * 60 - text[1]) * 2 + 170
            else:
                score = (4 * 60 + 40 - text[0] * 60 - text[1] - 1) * 2 + 171
            bot.send_message(message.from_user.id, f'Это {score} {forms[score % 10]}\nЦена секунды - 2',
                             reply_markup=biatl_run_menu)
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=biatl_run_menu)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=biatl_run_menu)


def tri_run(message):
    text = message.text
    tri_run_menu = types.InlineKeyboardMarkup()
    tri_run_try_again = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='run_tri')
    tri_run_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='run')
    tri_run_menu.add(tri_run_try_again)
    tri_run_menu.add(tri_run_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) in [2, 3]:
            score = 10 * 60 + 30 - text[0] * 60 - text[1] + 500
            bot.send_message(message.from_user.id, f'это {score} {forms[score % 10]}\nСтоимость секунды - 1',
                             reply_markup=tri_run_menu)
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=tri_run_menu)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=tri_run_menu)


def tetr_run(message):
    text = message.text
    tetr_run_menu = types.InlineKeyboardMarkup()
    tetr_run_try_again = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='run_tetr')
    tetr_run_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='run')
    tetr_run_menu.add(tetr_run_try_again)
    tetr_run_menu.add(tetr_run_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 2:
            score = 13 * 60 + 20 - text[0] * 60 - text[1] + 500
            bot.send_message(message.from_user.id, f'это {score} {forms[score % 10]}\nСтоимость секунды - 1',
                             reply_markup=tetr_run_menu)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=tetr_run_menu)


def ocr(message):
    text = message.text
    ocr_menu = types.InlineKeyboardMarkup()
    ocr_try_again = types.InlineKeyboardButton('попробуй ещё раз', callback_data='obstacles')
    ocr_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='choose')
    ocr_menu.add(ocr_try_again)
    ocr_menu.add(ocr_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 3:
            if text[2] == 0:
                score = (190 - text[0] * 60 - text[1]) * 2
            elif text[2] <= 50:
                score = (190 - text[0] * 60 - text[1]) * 2 - 1
            else:
                score = (190 - text[0] * 60 - text[1] - 1) * 2
            bot.send_message(message.from_user.id, f'Это {score} {forms[score % 10]}\nСтоимость секунды - 2',
                             reply_markup=ocr_menu)
            return 0
        if len(text) == 2:
            if text[1] <= 50:
                score = (190 - text[0]) * 2 - 1
            else:
                score = (190 - text[0] - 1) * 2
            bot.send_message(message.from_user.id, f'Это {score} {forms[score % 10]}\nСтоимость секунды - 2',
                             reply_markup=ocr_menu)
            return 0
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=ocr_menu)


def biatl(message):
    global score_biatl
    text = message.text
    if text_preprocessing(text):
        text = text_preprocessing(text)
    else:
        pass
    text = [int(i) for i in text]
    swim_menu_100m = types.InlineKeyboardMarkup()
    try_again_100m = types.InlineKeyboardButton(text='✍️ посчитать ещё раз ✍️', callback_data='biatl')
    get_back_100_200m = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='types')
    swim_menu_100m.add(try_again_100m)
    swim_menu_100m.add(get_back_100_200m)
    if len(text) == 3:
        if text[2] <= 50:
            score_biatl = (80 - text[0] * 60 - text[1]) * 4 + 250
        else:
            score_biatl = (80 - text[0] * 60 - text[1] - 1) * 4 + 252
        bot.send_message(message.from_user.id, 'введи время бега с сотыми')
        bot.register_next_step_handler(message, biatl_2nd_part)
    elif len(text) == 2 and text[0] > 40:
        if text[1] <= 50:
            score_biatl = (80 - text[0]) * 4 + 250
        else:
            score_biatl = (80 - text[0] - 1) * 4 + 252
        bot.send_message(message.from_user.id, 'введи время бега с сотыми')
        bot.register_next_step_handler(message, biatl_2nd_part)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_100m)
        return 0


def biatl_2nd_part(message):
    global score_biatl
    text = message.text
    biatl_run_menu = types.InlineKeyboardMarkup()
    biatl_run_again = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='biatl')
    biatl_run_get_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='types')
    biatl_run_menu.add(biatl_run_again)
    biatl_run_menu.add(biatl_run_get_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 3:
            if text[2] == 0:
                score = (4 * 60 + 40 - text[0] * 60 - text[1]) * 2 + 171
            elif text[2] <= 50:
                score = (4 * 60 + 40 - text[0] * 60 - text[1]) * 2 + 170
            else:
                score = (4 * 60 + 40 - text[0] * 60 - text[1] - 1) * 2 + 171
            bot.send_message(message.from_user.id, f'очков за плавание:\n{score_biatl}\nочков за бег:\n{score}\nсуммарно это {(score_biatl+score)} {forms[(score_biatl+score) % 10]}',
                             reply_markup=biatl_run_menu)
            score_biatl = 0
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=biatl_run_menu)
            score_biatl = 0
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=biatl_run_menu)
        score_biatl = 0


def triatl(message):
    global score_triatl
    text = message.text
    swim_menu_200m = types.InlineKeyboardMarkup()
    try_again_200m = types.InlineKeyboardButton(text='✍️ посчитать ещё раз ✍️', callback_data='triatl')
    get_back_100_200m = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='types')
    swim_menu_200m.add(try_again_200m)
    swim_menu_200m.add(get_back_100_200m)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 3:
            if text[2] <= 50:
                score_triatl = (238 - text[0] * 60 - text[1]) * 2 + 74
            else:
                score_triatl = (238 - text[0] * 60 - text[1] - 1) * 2 + 75
            bot.send_message(message.from_user.id, 'введи время лазер-рана')
            bot.register_next_step_handler(message, triatl_2nd_part)
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_200m)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_200m)


def triatl_2nd_part(message):
    global score_triatl
    text = message.text
    tri_run_menu = types.InlineKeyboardMarkup()
    tri_run_try_again = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='triatl')
    tri_run_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='types')
    tri_run_menu.add(tri_run_try_again)
    tri_run_menu.add(tri_run_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) in [2, 3]:
            score = 10 * 60 + 30 - text[0] * 60 - text[1] + 500
            bot.send_message(message.from_user.id, f'очков за плавание:\n{score_triatl}\nочков за лазер-ран:\n{score}\nсуммарно это {(score_triatl+score)} {forms[(score_triatl+score) % 10]}',
                             reply_markup=tri_run_menu)
            score_triatl = 0
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=tri_run_menu)
            score_triatl = 0
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=tri_run_menu)
        score_triatl = 0


def tetratl(message):
    global score_tetratl_1
    fence_menu = types.InlineKeyboardMarkup()
    try_again_fence = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='tetratl')
    get_back_fencing = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='types')
    fence_menu.add(try_again_fence)
    fence_menu.add(get_back_fencing)
    text = message.text
    if len(text.split('/')) > 1 or len(text.split()) > 1:
        if text_preprocessing(text):
            wins, losses = map(int, text_preprocessing(text))
        else:
            wins = losses = 0
        matches = wins + losses
        score_of_250 = one_win_score = 0
        fence_scores = list(csv.reader(open('fence_scores.csv')))
        for i in range(len(fence_scores)):
            fence_scores[i] = [int(j) for j in fence_scores[i][0].split(';')]
            if fence_scores[i][1] == matches:
                one_win_score = fence_scores[i][2]
                score_of_250 = fence_scores[i][0]
        score_tetratl_1 = 250 - (score_of_250 - wins) * one_win_score
        if score_of_250 > 0:
            bot.send_message(message.from_user.id, 'введи время плавания с сотыми')
            bot.register_next_step_handler(message, tetratl_2nd_part)
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=fence_menu)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=fence_menu)


def tetratl_2nd_part(message):
    global score_tetratl_1, score_tetratl_2
    text = message.text
    swim_menu_200m = types.InlineKeyboardMarkup()
    try_again_200m = types.InlineKeyboardButton(text='✍️ посчитать ещё раз ✍️', callback_data='tetratl')
    get_back_100_200m = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='types')
    swim_menu_200m.add(try_again_200m)
    swim_menu_200m.add(get_back_100_200m)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 3:
            if text[2] <= 50:
                score_tetratl_2 = (238 - text[0] * 60 - text[1]) * 2 + 74
            else:
                score_tetratl_2 = (238 - text[0] * 60 - text[1] - 1) * 2 + 75
            bot.send_message(message.from_user.id, 'введи время лазер-рана')
            bot.register_next_step_handler(message, tetratl_3rd_part)
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_200m)
            score_tetratl_1 = 0
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_200m)
        score_tetratl_1 = 0


def tetratl_3rd_part(message):
    global score_tetratl_1, score_tetratl_2
    text = message.text
    tetr_run_menu = types.InlineKeyboardMarkup()
    tetr_run_try_again = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='tetratl')
    tetr_run_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='types')
    tetr_run_menu.add(tetr_run_try_again)
    tetr_run_menu.add(tetr_run_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) in [2, 3]:
            score = 13 * 60 + 20 - text[0] * 60 - text[1] + 500
            bot.send_message(message.from_user.id, f'очков за фехтование:\n{score_tetratl_1}\nочков за плавание:\n{score_tetratl_2}\nочков за лазер-ран:\n{score}\nсуммарно это {(score_tetratl_1+score_tetratl_2+score)} {forms[(score_tetratl_1+score_tetratl_2+score) % 10]}',
                             reply_markup=tetr_run_menu)
            score_tetratl_1 = score_tetratl_2 = 0
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=tetr_run_menu)
        score_tetratl_1 = score_tetratl_2 = 0


def pentatl(message):
    global score_pentatl_1
    fence_menu = types.InlineKeyboardMarkup()
    try_again_fence = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='pentatl')
    get_back_fencing = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='types')
    fence_menu.add(try_again_fence)
    fence_menu.add(get_back_fencing)
    text = message.text
    if len(text.split('/')) > 1 or len(text.split()) > 1:
        if text_preprocessing(text):
            wins, losses = map(int, text_preprocessing(text))
        else:
            wins = losses = 0
        matches = wins + losses
        score_of_250 = one_win_score = 0
        fence_scores = list(csv.reader(open('fence_scores.csv')))
        for i in range(len(fence_scores)):
            fence_scores[i] = [int(j) for j in fence_scores[i][0].split(';')]
            if fence_scores[i][1] == matches:
                one_win_score = fence_scores[i][2]
                score_of_250 = fence_scores[i][0]
        score_pentatl_1 = 250 - (score_of_250 - wins) * one_win_score
        if score_of_250 > 0:
            bot.send_message(message.from_user.id, 'введи время плавания с сотыми')
            bot.register_next_step_handler(message, pentatl_2nd_part)
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=fence_menu)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=fence_menu)


def pentatl_2nd_part(message):
    global score_pentatl_1, score_pentatl_2
    text = message.text
    swim_menu_200m = types.InlineKeyboardMarkup()
    try_again_200m = types.InlineKeyboardButton(text='✍️ посчитать ещё раз ✍️', callback_data='pentatl')
    get_back_100_200m = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='types')
    swim_menu_200m.add(try_again_200m)
    swim_menu_200m.add(get_back_100_200m)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 3:
            if text[2] <= 50:
                score_pentatl_2 = (238 - text[0] * 60 - text[1]) * 2 + 74
            else:
                score_pentatl_2 = (238 - text[0] * 60 - text[1] - 1) * 2 + 75
            bot.send_message(message.from_user.id, 'введи время лазер-рана')
            bot.register_next_step_handler(message, pentatl_3rd_part)
        else:
            bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_200m)
            score_pentatl_1 = 0
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=swim_menu_200m)
        score_pentatl_1 = 0


def pentatl_3rd_part(message):
    global score_pentatl_1, score_pentatl_2, score_pentatl_3
    text = message.text
    tetr_run_menu = types.InlineKeyboardMarkup()
    tetr_run_try_again = types.InlineKeyboardButton('✍️ посчитать ещё раз ✍️', callback_data='pentatl')
    tetr_run_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='types')
    tetr_run_menu.add(tetr_run_try_again)
    tetr_run_menu.add(tetr_run_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) in [2, 3]:
            score_pentatl_3 = 13 * 60 + 20 - text[0] * 60 - text[1] + 500
            bot.send_message(message.from_user.id, 'введи время прохождения полосы с сотыми')
            bot.register_next_step_handler(message, pentatl_4th_part)
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=tetr_run_menu)
        score_pentatl_1 = score_pentatl_2 = 0


def pentatl_4th_part(message):
    global score_pentatl_1, score_pentatl_2, score_pentatl_3
    text = message.text
    ocr_menu = types.InlineKeyboardMarkup()
    ocr_try_again = types.InlineKeyboardButton('попробуй ещё раз', callback_data='pentatl')
    ocr_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='types')
    ocr_menu.add(ocr_try_again)
    ocr_menu.add(ocr_back)
    if text_preprocessing(text):
        text = text_preprocessing(text)
        text = [int(i) for i in text]
        if len(text) == 3:
            if text[2] == 0:
                score = (190 - text[0] * 60 - text[1]) * 2
            elif text[2] <= 50:
                score = (190 - text[0] * 60 - text[1]) * 2 - 1
            else:
                score = (190 - text[0] * 60 - text[1] - 1) * 2
            bot.send_message(message.from_user.id, f'очков за фехтование:\n{score_pentatl_1}\nочков за плавание:\n{score_pentatl_2}\nочков за лазер-ран:\n{score_pentatl_3}\nочков за полосу препятствий:\n{score}\nсуммарно это {(score_pentatl_1+score_pentatl_2+score_pentatl_3+score)} {forms[(score_pentatl_1+score_pentatl_2+score_pentatl_3+score) % 10]}',
                             reply_markup=ocr_menu)
            return 0
        if len(text) == 2:
            if text[1] <= 50:
                score = (190 - text[0]) * 2 - 1
            else:
                score = (190 - text[0] - 1) * 2
            bot.send_message(message.from_user.id,
                             f'очков за фехтование:\n{score_pentatl_1}\nочков за плавание:\n{score_pentatl_2}\nочков за лазер-ран:\n{score_pentatl_3}\nочков за полосу препятствий:\n{score}\nсуммарно это {(score_pentatl_1 + score_pentatl_2 + score_pentatl_3 + score)} {forms[(score_pentatl_1 + score_pentatl_2 + score_pentatl_3 + score) % 10]}',
                             reply_markup=ocr_menu)
            return 0
    else:
        bot.send_message(message.from_user.id, 'попробуй ещё раз', reply_markup=ocr_menu)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'help':
        help_menu = types.InlineKeyboardMarkup()
        about_format = types.InlineKeyboardButton('⏱️ формат ввода данных ⏱️', callback_data='about_types')
        about_sources = types.InlineKeyboardButton('🧐 используемые ресурсы 🧐', callback_data='sources')
        get_back_help = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='back')
        for i in [about_format, about_sources, get_back_help]:
            help_menu.add(i)
        bot.send_message(call.message.chat.id, 'меню помощи', reply_markup=help_menu)
    if call.data == 'choose':
        disciplines = types.InlineKeyboardMarkup()
        swim = types.InlineKeyboardButton(text='🏊🏻‍♀️ плавание 🏊🏻', callback_data='swim')
        fencing = types.InlineKeyboardButton(text='🤺 фехтование 🤺', callback_data='fencing')
        run = types.InlineKeyboardButton(text='🏃🏻 бег 🏃🏻', callback_data='run')
        obstacles = types.InlineKeyboardButton(text='🧗🏻‍ ️полоса препятствий 🧱', callback_data='obstacles')
        get_back = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='back')
        for i in [swim, fencing, run, obstacles, get_back]:
            disciplines.add(i)
        bot.send_message(call.message.chat.id, text='выбери вид', reply_markup=disciplines)
    if call.data == 'back':
        keyboard = types.InlineKeyboardMarkup()
        dicsipline_choice = types.InlineKeyboardButton(text='📋 выбор вида 📋', callback_data='choose')
        discipline_choice = types.InlineKeyboardButton(text='📑 выбор дисциплины 📑', callback_data='types')
        keyboard.add(discipline_choice)
        keyboard.add(dicsipline_choice)
        help_about = types.InlineKeyboardButton(text='📣 помощь 📣', callback_data='help')
        keyboard.add(help_about)
        bot.send_photo(call.message.chat.id, photo=open('logo.png', 'rb'), caption='меню', reply_markup=keyboard)
    if call.data == 'swim':
        swim_menu = types.InlineKeyboardMarkup()
        hundred_meters = types.InlineKeyboardButton(text='100м', callback_data='100m')
        two_hundred_meters = types.InlineKeyboardButton(text='200м', callback_data='200m')
        get_to_disciplines = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='choose')
        swim_menu.add(hundred_meters)
        swim_menu.add(two_hundred_meters)
        swim_menu.add(get_to_disciplines)
        bot.send_message(call.message.chat.id, text='выбери дистанцию', reply_markup=swim_menu)
    if call.data == '100m':
        bot.send_message(call.message.chat.id, text='введи время с сотыми')
        bot.register_next_step_handler(call.message, get_time_100)
    if call.data == '200m':
        bot.send_message(call.message.chat.id, text='введи время с сотыми')
        bot.register_next_step_handler(call.message, get_time_200)
    if call.data == 'fencing':
        bot.send_message(call.message.chat.id, text='введи количество побед / проигрышей')
        bot.register_next_step_handler(call.message, get_fence_score)
    if call.data == 'run':
        run_menu = types.InlineKeyboardMarkup()
        run_tri = types.InlineKeyboardButton('4 * 600 со стрельбой', callback_data='run_tri')
        run_tetr = types.InlineKeyboardButton('5 * 600 со стрельбой', callback_data='run_tetr')
        run_bia = types.InlineKeyboardButton('1000 м', callback_data='1000m')
        get_to_menu = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='choose')
        for i in [run_bia, run_tri, run_tetr, get_to_menu]:
            run_menu.add(i)
        bot.send_message(call.message.chat.id, text='выбери дистанцию', reply_markup=run_menu)
    if call.data == 'run_tri':
        bot.send_message(call.message.chat.id, text='введи время')
        bot.register_next_step_handler(call.message, tri_run)
    if call.data == 'run_tetr':
        bot.send_message(call.message.chat.id, text='введи время')
        bot.register_next_step_handler(call.message, tetr_run)
    if call.data == '1000m':
        bot.send_message(call.message.chat.id, text='введи время с сотыми')
        bot.register_next_step_handler(call.message, biatl_run)
    if call.data == 'obstacles':
        bot.send_message(call.message.chat.id, text='введи время с сотыми')
        bot.register_next_step_handler(call.message, ocr)
    if call.data == 'sources':
        sources_menu = types.InlineKeyboardMarkup()
        source_1 = types.InlineKeyboardButton('правила вида спорта', url='https://pentathlon-russia.ru/files/rmisbh-pravila-sovremennoe-pyatibore-2022-okonchatelno.pdf')
        source_2 = types.InlineKeyboardButton('obstacle discipline', url='https://www.uipmworld.org/sites/default/files/uipm_od_comp_guidelines_final_3.pdf')
        source_3 = types.InlineKeyboardButton('сайт федерации', url='https://www.pentathlon-russia.ru/')
        source_get_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='help')
        sources_menu.add(source_1)
        sources_menu.add(source_2)
        sources_menu.add(source_3)
        sources_menu.add(source_get_back)
        bot.send_message(call.message.chat.id, text='Текст правил ФСПР и UIPM', reply_markup=sources_menu)
    if call.data == 'about_types':
        about_types_menu = types.InlineKeyboardMarkup()
        about_types_back = types.InlineKeyboardButton('перейти назад  ↩️', callback_data='help')
        about_types_menu.add(about_types_back)
        bot.send_message(call.message.chat.id,
                         text='Формат ввода времени плавания / бега на 1000 м / прохождения полосы:\nминуты.секунды.сотые\nФормат ввода времени лазер-рана:\nминуты.секунды\nФормат ввода результатов фехтования:\nпобеды / проигрыши',
                         reply_markup=about_types_menu)
    if call.data == 'types':
        types_menu = types.InlineKeyboardMarkup()
        types_biatl = types.InlineKeyboardButton('🏊🏻‍ двоеборье 🏃🏻', callback_data='biatl')
        types_triatl = types.InlineKeyboardButton('🏊🏻‍ троеборье 🔫🏃🏻', callback_data='triatl')
        types_tetratl = types.InlineKeyboardButton('🏊🏻‍🤺 четырёхборье 🔫🏃🏻', callback_data='tetratl')
        types_pentatl = types.InlineKeyboardButton('🏊🏻‍🤺 пятиборье 🔫🏃🏻🧗🏻', callback_data='pentatl')
        types_get_back = types.InlineKeyboardButton(text='перейти назад  ↩️', callback_data='back')
        for i in [types_biatl, types_triatl, types_tetratl, types_pentatl, types_get_back]:
            types_menu.add(i)
        bot.send_message(call.message.chat.id, 'выбери дисциплину', reply_markup=types_menu)
    if call.data == 'biatl':
        bot.send_message(call.message.chat.id, 'введи время плавания с сотыми')
        bot.register_next_step_handler(call.message, biatl)
    if call.data == 'triatl':
        bot.send_message(call.message.chat.id, 'введи время плавания с сотыми')
        bot.register_next_step_handler(call.message, triatl)
    if call.data == 'tetratl':
        bot.send_message(call.message.chat.id, 'введи количество побед / проигрышей')
        bot.register_next_step_handler(call.message, tetratl)
    if call.data == 'pentatl':
        bot.send_message(call.message.chat.id, 'введи количество побед / проигрышей')
        bot.register_next_step_handler(call.message, pentatl)


bot.polling(none_stop=True, interval=0)
