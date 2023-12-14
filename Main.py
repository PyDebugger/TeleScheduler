import json
import telebot
from telebot import types
import re
import time
from threading import Thread
import assemblyai as aai

bot = telebot.TeleBot('MY_TOKEN')


# ----- Путь к файлу для хранения данных ------ #
data_file = "ivent.json"
one_time_events_file = "iventFast.json"
# --------------------------------------------- #

# --------------------------------------------- #
var_schedule = []
now_time_user = "Выберите время: \n Ваше время: "

# -------------Статусы ------------------ #
status_ivent = False
STATUS_DELETE = False
# --------------------------------------- #

count_numbering = None
selected_time_user = ""
days_of_week = [["Понедельник", "Monday","Дүйсенбі"], ["Вторник", "Tuesday","Сейсенбі"], ["Среда", "Wednesday","Сәрсенбі"], ["Четверг", "Thursday","Бейсенбі"],
                    ["Пятница", "Friday","Жұма"], ["Суббота", "Saturday","Сенбі"], ["Воскресенье", "Sunday","Жексенбі"]]
number = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", '5️⃣', "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

ivent_user_voice = []

number_dict = {
    'ноль': 0, 'один': 1, 'два': 2, 'три': 3, 'четыре': 4,
    'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9,
    'десять': 10, 'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14,
    'пятнадцать': 15, 'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19,
    'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,
}

# ------------------- Данные из файла language.json ------------------- #
with open('language.json', 'r', encoding='utf-8') as file:
    dict_lang = json.load(file)
# --------------------------------------------------------------------- #


# ---------- загрузка данных в файл данных о пользователях -------------#
def load_data_user():
    with open('data_user.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# Сохранение данных в файл данных о пользователях
def save_data_user(data_user):
    with open('data_user.json', 'w', encoding='utf-8') as file:
        json.dump(data_user, file, ensure_ascii=False, indent=4)
# --------------------------------------------------------------------- #


# # Загрузка данных и сохранение файла json с регулярными событиями
def load_user_data():
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
def save_user_data(user_data):
    with open(data_file, 'w') as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)
# --------------------------------------------- #

# Загрузка данных и сохранение файла json с разовыми событиями
def load_one_time_events():
    try:
        with open(one_time_events_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
def save_one_time_events(one_time_events):
    with open(one_time_events_file, 'w') as file:
        json.dump(one_time_events, file, ensure_ascii=False, indent=4)
# --------------------------------------------- #


# ----------------------------Удаление пользователя, если у него пустые события ------------------- #
def remove_empty_events(UserId):
    data_schedule = load_user_data()
    if UserId in data_schedule:
        check_user_data = lambda user_id: [True for ivent in data_schedule[user_id] if ivent]
        if not check_user_data(UserId):
            data_schedule.pop(UserId)
            save_user_data(data_schedule)
# ------------------------------------------------------------------------------------------------ #

#============================= Обработчик для предложения зараннее упоминания ==============================#
def time_mention(user_id):
    lang = load_data_user()[str(user_id)]["lang"] # загрузить данные и получить язык пользователя
    keyboard = types.InlineKeyboardMarkup()
    button_time_all = [types.InlineKeyboardButton(text=str(time_H), callback_data="callback_time_before_" + str(time_H)) for time_H in range(0,61,15)]
    keyboard.add(*button_time_all)
    bot.send_message(user_id, dict_lang["Time_before_event"][lang], reply_markup=keyboard)
# =========================================================================================================#

# ========================== обработчик команды /start ======================================== #
@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIT_GVvDhj_iIyQgdIQ6IkRMkgJlYaqAAI2FgACcmugS6XaTV2HP2QpMwQ')
    # предлагает выбрать язык бота
    keyboard = types.InlineKeyboardMarkup()
    buttonRu = types.InlineKeyboardButton(text="🇷🇺", callback_data="ru")
    buttonEn = types.InlineKeyboardButton(text="🇺🇸", callback_data="en")
    buttonKz = types.InlineKeyboardButton(text="🇰🇿", callback_data="kz")
    keyboard.add(buttonRu, buttonEn, buttonKz)
    bot.send_message(message.chat.id, "Select bot language: ", reply_markup=keyboard, parse_mode='html')

# ============================================================================================= #

# ===================================== НАЧАЛЬНОЕ МЕНЮ ======================================== #
def start(message):
    lang = load_data_user()[str(message.chat.id)]["lang"] # загрузить данные  и получить язык пользователя

    #lang = data_user[str(message.chat.id)]["lang"] # получить язык пользователя

    keyboard,user_id = types.InlineKeyboardMarkup(), message.chat.id
    add_schedule = types.InlineKeyboardButton(text = dict_lang['Add_schedule'][lang],     callback_data="add_schedule")
    view_all_schedule = types.InlineKeyboardButton(text = dict_lang['View_schedule'][lang], callback_data="view_all_schedule")
    delete_all_schedule = types.InlineKeyboardButton(text = dict_lang['Delete_schedule'][lang],   callback_data="delete_all_schedule")
    keyboard.add(add_schedule);keyboard.add(view_all_schedule);keyboard.add(delete_all_schedule)

    # view_schedule = types.InlineKeyboardButton(text="📋Регулярные события📋", callback_data="view_schedule")
    # view_schedule_one_time = types.InlineKeyboardButton(text="📋Разовые события📋", callback_data="view_schedule_one_time")
    # delete_schedule = types.InlineKeyboardButton(text="❌Регулярные события❌",   callback_data="delete_schedule")
    # delete_schedule_one_time = types.InlineKeyboardButton(text="❌Разовые события❌",   callback_data="delete_schedule_one_time")
    # keyboard.add(add_schedule);keyboard.add(view_schedule,view_schedule_one_time);keyboard.add(delete_schedule,delete_schedule_one_time)
    bot.send_message(user_id, dict_lang['greetings'][lang], reply_markup=keyboard)
# ============================================================================================= #


# ===================================  КНОПКИ ВРЕМЕНИ ======================================= #
def button_time(user_id,time_user):
    lang = load_data_user()[str(user_id)]["lang"] # загрузить данные  и получить язык пользователя

    keyboard = types.InlineKeyboardMarkup()
    buttonTimeHour = [types.InlineKeyboardButton(text=str(time_H), callback_data = "callback_" + str(time_H)) for time_H in range(1,10)]
    keyboard.add(*buttonTimeHour)
    keyboard.add(types.InlineKeyboardButton(text="0", callback_data="callback_0"))
    keyboard.add(types.InlineKeyboardButton(text=dict_lang["cancel"][lang], callback_data="callback_cancel"))
    bot.send_message(user_id, time_user, reply_markup=keyboard)
# ============================================================================================= #

# ============================ ОБРАБОТЧИК ВСЕХ CALLBACK кнопок ============================== #
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call): # функция обработки callback кнопок (нажатие на кнопку)
    global dict_lang,data_user
# --------------------------- Кнопки выбора языка -------------------------- #
    if call.data in ["ru", "en", "kz"]: # если нажата кнопка с языком
        bot.delete_message(call.message.chat.id, call.message.message_id)
        data_user = load_data_user() # загрузить данные о пользователе

        if str(call.message.chat.id) not in data_user:
            data_user[str(call.message.chat.id)] = {} # добавить пользователя в файл с языком

        data_user[str(call.message.chat.id)]["lang"] = call.data # добавить пользователя в файл с языком
        save_data_user(data_user) # сохранить данные о пользователе

        start(call.message) # вызвать функцию начального меню

    global selected_time_user # глобальная переменная для хранения времени пользователя
    global STATUS_DELETE,count_numbering # глобальная переменная для хранения статуса удаления события
    lang = load_data_user()[str(call.message.chat.id)]["lang"] # загрузить данные и получить язык пользователя

# --------------------------- Кнопка добавить расписание -------------------------- #
    if call.data == "add_schedule": # если нажата кнопка "Добавить расписание"
        add_schedule(call.message) # вызвать функцию добавления расписания

# --------------------------- Выбор дня недели ------------------------------------ #
    now_time_user = dict_lang["Select_time"][lang] + '\n' + dict_lang["Your_time"][lang] # получить текст с выбором дня недели

    if call.data in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]: # если нажата кнопка с днем недели
        var_schedule.clear() # очистить список
        var_schedule.append(call.data) # добавить день недели в список
        button_time(call.message.chat.id,now_time_user) # вызвать функцию выбора времени

# --------------------------- Выбор времени ------------------------------------ #
    if call.data in ["callback_" + str(time_H) for time_H in range(0,10)]: # если нажата кнопка с временем
        selected_time_user += call.data[-1] # добавить выбранное время к времени пользователя
        bot.delete_message(call.message.chat.id, call.message.message_id) # удалить сообщение с выбором времени

    # --------------------------- Сохранение выбранного времени ------------------------------------ #
        if len(selected_time_user) < 5: # если введено меньше 5 символов
            if len(selected_time_user) == 2: # если введено две цифры
                selected_time_user += ":" # добавить двоеточие
            button_time(call.message.chat.id,now_time_user + selected_time_user) # вернуть к выбору времени

    # ---------------------------- Проверить время на корректность --------------------------------- #
        if len(selected_time_user) == 5: # если время введено полностью
            if int(selected_time_user.split(':')[0]) > 23 or int(selected_time_user.split(':')[1]) > 59: # если время введено некорректно
                bot.send_message(call.message.chat.id, dict_lang["Incorrect_time"][lang]) # отправить сообщение с ошибкой
                selected_time_user = "" # обнулить выбранное время
                button_time(call.message.chat.id,now_time_user) # вернуть к выбору времени
            else: # если время введено корректно
                bot.send_message(call.message.chat.id, dict_lang["Your_time"][lang] + selected_time_user) # отправить сообщение с выбранным временем
                var_schedule.append(selected_time_user) # добавить время в список
                selected_time_user = ""  # обнулить выбранное время
                # вызов обработчика ввода события
                add_event(call.message) # вызвать функцию ввода события
# =========================================================================================== #


# --------------------------- Кнопка отмены и сохранения -------------------------- #
    if call.data == "callback_cancel_save": # отмена сохранения события
        var_schedule.clear() # очистить список
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message) # вернуть к начальному меню
    if call.data == "callback_save":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        time_mention(call.message.chat.id)

# --------------------------- Кнопка заранее упоминания пользователя -------------------------- #
    if call.data in ["callback_time_before_" + str(time_H) for time_H in range(0,61,5)]: # если нажата кнопка с временем
        bot.delete_message(call.message.chat.id, call.message.message_id)
        var_schedule.append(call.data[21:]) # добавить время в список
        bot.send_message(call.message.chat.id, dict_lang["Saving_regular_event"][lang])

        load_user_schedule(call.message.chat.id) # загрузить событие к пользователю в файл


# --------------------------- Кнопка просмотра расписания -------------------------- #
    if call.data == "view_all_schedule":
        # показать две кнопки с выбором просмотра расписания
        keyboard = types.InlineKeyboardMarkup()
        buttonRegular = types.InlineKeyboardButton(text=dict_lang["Regular_event"][lang], callback_data="view_schedule")
        buttonOneTime = types.InlineKeyboardButton(text=dict_lang["One_time_event"][lang], callback_data="view_schedule_one_time")
        keyboard.add(buttonRegular);keyboard.add(buttonOneTime)
        bot.send_message(call.message.chat.id, dict_lang["select_event_type"][lang], reply_markup=keyboard) # отправить сообщение с кнопками

# --------------------------- Кнопка просмотра регулярных событий -------------------------- #
    if call.data == "view_schedule": # если нажата кнопка "Просмотреть расписание"
        remove_empty_events(str(call.message.chat.id)) # удалить пользователя из файла, если у него нет событий
        show_all_schedule(call.message.chat.id, False,"regular") # вызвать функцию просмотра расписания
        start(call.message) # вернуть к начальному меню
# --------------------------- Кнопка просмотра разовых событий -------------------------- #
    if call.data == "view_schedule_one_time": # если нажата кнопка "Просмотреть разовые события"
        show_all_schedule(call.message.chat.id, False,"one_time") # вызвать функцию просмотра разовых событий
        start(call.message) # вернуть к начальному меню
    if call.data == "delete_all_schedule": # если нажата кнопка "Удалить расписание"
        # показать две кнопки с выбором удаления расписания
        keyboard = types.InlineKeyboardMarkup()
        buttonRegular = types.InlineKeyboardButton(text=dict_lang["Regular_event"][lang], callback_data="delete_schedule")
        buttonOneTime = types.InlineKeyboardButton(text=dict_lang["One_time_event"][lang], callback_data="delete_schedule_one_time")
        keyboard.add(buttonRegular);keyboard.add(buttonOneTime)
        bot.send_message(call.message.chat.id,  dict_lang["select_event_type"][lang], reply_markup=keyboard) # отправить сообщение с кнопками


# --------------------------- Кнопка удаления расписания -------------------------- #
    if call.data == "delete_schedule": # Действие "Удалить расписание"
        remove_empty_events(str(call.message.chat.id)) # удалить пользователя из файла, если у него нет событий

        try:
            keyboard = types.InlineKeyboardMarkup()
            count_numbering = show_all_schedule(call.message.chat.id, True,"regular") # вызвать функцию просмотра расписания с номерацией событий
            # создать кнопки с номерами событий
            button_numbering = [types.InlineKeyboardButton(text=str(numbering), callback_data="callbackDel_" + str(numbering)) for numbering in range(1, count_numbering + 1)]
            keyboard.add(*button_numbering)

            STATUS_DELETE = True # установить статус удаления события
            bot.send_message(call.message.chat.id, dict_lang["Number_event_delete"][lang], reply_markup=keyboard) # отправить сообщение с кнопками
        except: # если расписания нет
            bot.send_message(call.message.chat.id, dict_lang["lack_schedule"][lang])

# --------------------------- Кнопка удаления события -------------------------- #
    if STATUS_DELETE == True and call.data in ["callbackDel_" + str(numbering) for numbering in range(1, count_numbering + 1)]:
        STATUS_DELETE = False # сбросить статус удаления события
        bot.delete_message(call.message.chat.id, call.message.message_id) # удалить сообщение с кнопками
        data_schedule = load_user_data() # загрузить расписание пользователя
        if str(call.message.chat.id) in data_schedule: # Проверка наличия пользователя в файле
            find_numbering = find_numbering_schedule(str(call.message.chat.id), int(call.data[12:]),type_schedule="regular")  # Поиск номера события
            if find_numbering != False: # Если номер события найден
                weekday, numbering = find_numbering # Присвоение переменным значения из функции find_numbering_schedule
                del data_schedule[str(call.message.chat.id)][weekday][numbering] # Удаление события из расписания
                save_user_data(data_schedule) # Сохранение расписания
                bot.send_message(call.message.chat.id, dict_lang["Deleting_event"][lang]) # Отправка сообщения о удалении события
                start(call.message) # Возврат к начальному меню
            elif find_numbering == False: # Если номер события не найден
                bot.send_message(call.message.chat.id, dict_lang["Incorrect_number_event"][lang])
                start(call.message)
        else: # Если пользователя нет в файле
            bot.send_message(call.message.chat.id, dict_lang["lack_schedule"][lang])
            start(call.message)

# --------------------------- Кнопка удаления разового события -------------------------- #
    if  call.data == "delete_schedule_one_time" : # Действие "Удалить разовое событие"
        STATUS_DELETE = True  # установить статус удаления события
        count_numbering = show_all_schedule(call.message.chat.id,True,"one_time")  # вызвать функцию просмотра расписания с номерацией событий
        one_time_events = load_one_time_events() # загрузить разовые события
        if str(call.message.chat.id) in one_time_events: # если пользователь есть в файле
            keyboard = types.InlineKeyboardMarkup()
#             # создать кнопки с номерами событий
            button_numbering = [types.InlineKeyboardButton(text=str(numbering), callback_data="callbackDelOneTime_" + str(numbering)) for numbering in range(1, count_numbering + 1)]
            keyboard.add(*button_numbering)
            bot.send_message(call.message.chat.id, dict_lang["Number_event_delete"][lang], reply_markup=keyboard) # отправить сообщение с кнопками
#
        else: # если пользователь не найден, то отправить сообщение
            bot.send_message(call.message.chat.id, dict_lang["you_dont_have_onte_time_event"][lang])
    try:
        if STATUS_DELETE == True and call.data in ["callbackDelOneTime_" + str(numbering) for numbering in range(1, count_numbering + 1)]:
            STATUS_DELETE == False # сбросить статус удаления события
            bot.delete_message(call.message.chat.id, call.message.message_id)
            one_time_events = load_one_time_events() # загрузить разовые события
            if str(call.message.chat.id) in one_time_events: # если пользователь есть в файле
                find_numbering = find_numbering_schedule(str(call.message.chat.id), int(call.data[19:]),type_schedule="one_time")  # Поиск номера события
                if find_numbering != False: # Если номер события найден
                    weekday, numbering = find_numbering # Присвоение переменным значения из функции find_numbering_schedule
                    del one_time_events[str(call.message.chat.id)][weekday][numbering] # Удаление события из разовых событий
                    save_one_time_events(one_time_events)
                    bot.send_message(call.message.chat.id, dict_lang["Deleting_event"][lang])  # Отправка сообщения о удалении события
                    start(call.message)  # Возврат к начальному меню
                elif find_numbering == False: # Если номер события не найден
                    bot.send_message(call.message.chat.id, dict_lang["Incorrect_number_event"][lang])
                    start(call.message)
            else: # если пользователь не найден, то отправить сообщение
                bot.send_message(call.message.chat.id, dict_lang["you_dont_have_onte_time_event"][lang])
                start(call.message)
    except: pass



# --------------------------- Кнопка отмены удаления события -------------------------- #
    if call.data == "callback_cancel": # отмена выбора времени
        bot.delete_message(call.message.chat.id, call.message.message_id) # удалить сообщение с выбором времени
        selected_time_user = "" # обнулить выбранное время
        start(call.message) # вернуть к начальному меню


# ============= ОБРАБОТЧИК CALLBACK КНОПОК ПО ГОЛОСОВЫМ СООБЩЕНИЯМ ==================== #
    if call.data == "callback_save_voice":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        data_schedule = load_user_data() # загрузить расписание пользователя
        try: # если день недели найден, значит это еженедельное событие
            index_weekday = [i for i in range(len(days_of_week)) if days_of_week[i][1] == ivent_user_voice[0]][0]  # получить индекс дня недели
            if str(call.message.chat.id) not in data_schedule:
                data_schedule[str(call.message.chat.id)] = [[], [], [], [], [], [], []]  # Добавление пользователя в файл с пустым расписанием

                data_schedule[str(call.message.chat.id)][index_weekday].append(
                    {"WeekDay": ivent_user_voice[0], "Time": ivent_user_voice[1],
                     "Event": ivent_user_voice[2],"time_before":"0"})  # Добавление события в расписание
            else:
                data_schedule[str(call.message.chat.id)][index_weekday].append(
                    {"WeekDay": ivent_user_voice[0], "Time": ivent_user_voice[1],
                     "Event": ivent_user_voice[2],"time_before":"0"})  # Добавление события в расписание
            save_user_data(data_schedule)  # сохранить расписание пользователя
            bot.send_message(call.message.chat.id, dict["Saving_regular_event"][lang])
            start(call.message) # вернуть к начальному меню

        except: # если день недели не найден, значит это разовое событие
            one_time_events = load_one_time_events()
            if str(call.message.chat.id) not in one_time_events:
                one_time_events[str(call.message.chat.id)] = [[]]
                one_time_events[str(call.message.chat.id)][0].append(
                    {"WeekDay": ivent_user_voice[0], "Time": ivent_user_voice[1],
                     "Event": ivent_user_voice[2]})
            else:
                one_time_events[str(call.message.chat.id)][0].append(
                    {"WeekDay": ivent_user_voice[0], "Time": ivent_user_voice[1],
                     "Event": ivent_user_voice[2]})
            save_one_time_events(one_time_events) # сохранить разовое событие
            bot.send_message(call.message.chat.id, dict_lang["Saving_OT_event"][lang])
            start(call.message) # вернуть к начальному меню


    if call.data == "callback_cancel_voice":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
# ==================================================================================== #


# ============================ обработчик текст события ============================== #
@bot.message_handler(commands=['add_event'])
def add_event(message):
    lang = load_data_user()[str(message.chat.id)]["lang"] # загрузить данные и получить язык пользователя
    global status_ivent
    bot.send_message(message.chat.id, dict_lang["Put_ivent"][lang])
    status_ivent = True # установить статус ввода события, чтобы обработчик ввода события сработал
# ==================================================================================== #


# ================================ обработчик ввода события ====================================== #
@bot.message_handler(func=lambda message: status_ivent == True, content_types=['text'])
def handle_enter_event(message):
    lang = load_data_user()[str(message.chat.id)]["lang"] # загрузить данные и получить язык пользователя

    global status_ivent # глобальная переменная для хранения статуса ввода события
    status_ivent = False # сбросить статус ввода события, чтобы обработчик ввода события не сработал
    var_schedule.append(message.text) # добавить событие в список
    keyboard = types.InlineKeyboardMarkup()
    buttonSave = types.InlineKeyboardButton(text=dict_lang["button_save"][lang], callback_data="callback_save")
    buttonCancel = types.InlineKeyboardButton(text=dict_lang["button_cancel"][lang], callback_data="callback_cancel_save")
    keyboard.add(buttonSave);keyboard.add(buttonCancel)
    ending_ivent = ""
    for i in range(len(days_of_week)): # перебор всех дней недели
        if var_schedule[0] in days_of_week[i]: # если день недели найден, то добавить его в переменную
            ending_ivent = dict_lang[days_of_week[i][1]][lang]
            break  # выйти из цикла
    # отправить сообщение с выбранным днем недели, временем и событием и указанием кнопок "Сохранить" и "Отмена" для подтверждения
    bot.send_message(message.chat.id, f'{dict_lang["question_save_event"][lang]} \n <b>{ending_ivent + " | " + var_schedule[1] + " | " + var_schedule[2]}</b>', reply_markup=keyboard, parse_mode='html')

# ==================================================================================== #



# =========== обработчик для отображения кнопок с выбором дня недели ============= #
@bot.message_handler(commands=['add_schedule'])
def add_schedule(message):
    lang = load_data_user()[str(message.chat.id)]["lang"] # загрузить данные и получить язык пользователя
    keyboard = types.InlineKeyboardMarkup()
    lang = load_data_user()[str(message.chat.id)]["lang"] # загрузить данные и получить язык пользователя
    index_lang = 1 if lang == "en" else 0 if lang == "ru" else 2
    buttonAll = [types.InlineKeyboardButton(text=day[index_lang], callback_data=day[1]) for day in days_of_week]
    keyboard.add(*buttonAll) # добавить кнопки с днями недели
    bot.send_message(message.chat.id, dict_lang["select_weekday"][lang], reply_markup=keyboard)
# ==================================================================================== #


# ======================== ДОБАВЛЕНИЕ СОБЫТИЯ В РАСПИСАНИЕ ================================
def load_user_schedule(user_id):
    data_schedule = load_user_data() # загрузить расписание пользователей
    index_weekday = [i for i in range(len(days_of_week)) if days_of_week[i][1] == var_schedule[0]][0] # получить индекс дня недели

    if str(user_id) not in data_schedule:
        data_schedule[str(user_id)] = [[], [], [], [], [], [], []] # Добавление пользователя в файл с пустым расписанием

        data_schedule[str(user_id)][index_weekday].append(
            {"WeekDay": var_schedule[0], "Time": var_schedule[1],
             "Event": var_schedule[2],"time_before":var_schedule[3]})  # Добавление события в расписание
    else:
        data_schedule[str(user_id)][index_weekday].append(
            {"WeekDay": var_schedule[0], "Time": var_schedule[1],
             "Event": var_schedule[2],"time_before":var_schedule[3]}) # Добавление события в расписание

    save_user_data(data_schedule) # сохранить расписание пользователя
    var_schedule.clear() # очистить список
# ==================================================================================== #

# ======================== ПРОСМОТР РАСПИСАНИЯ ================================
def show_all_schedule(user_id, on_numbering,type_schedule):
    lang = load_data_user()[str(user_id)]["lang"] # загрузить данные и получить язык пользователя
    if type_schedule == "regular":
        data_schedule = load_user_data() # загрузить расписание пользователя
    elif type_schedule == "one_time":
        data_schedule = load_one_time_events()

    #days_of_week_ru = [day[0] for day in days_of_week] # получить дни недели на русском
    if str(user_id) in data_schedule: # если пользователь есть в файле
        output = ""; count_numbering = 0 # переменные для хранения вывода и номера события
        for item, events in enumerate(data_schedule[str(user_id)]): # перебор всех дней недели
            if not events: continue # если событий нет, то продолжить цикл
            index_lang = 1 if lang == "en" else 0 if lang == "ru" else 2
            output += f"<u><b>{days_of_week[item][index_lang]}</b></u>:\n" # добавить день недели в вывод событий
            for idx, event in enumerate(events): # перебор всех событий
                # добавить в вывод время и событие, если включена нумерация
                if on_numbering: count_numbering += 1; out_numbering = f"<b><u>{count_numbering}</u></b>) "
                else: out_numbering = "" # иначе не добавлять нумерацию

                # ------------------ добавление времени и события в вывод ------------------ #

                output += f'{out_numbering}{number[int(event["Time"][0])]}{number[int(event["Time"][1])]}<b>:' \
                          f'</b>{number[int(event["Time"][3])]}{number[int(event["Time"][4])]} ' \
                          f' |_<u><i>{dict_lang["Ivent"][lang]}:</i>__{event["Event"]}</u> \n'
            bot.send_message(user_id, output, parse_mode="HTML")
            # ------------------------------------------------------------------------------ #
            output = "" # очистить вывод
        return count_numbering # вернуть номер события, для будущего удаления события
    else: bot.send_message(user_id, dict_lang["lack_schedule"][lang]) # если пользователь не найден, то отправить сообщение
# ==================================================================================== #


# ======================== ПОИСК НОМЕРА СОБЫТИЯ ================================ #
def find_numbering_schedule(user_id, number_schedule, type_schedule):
    if type_schedule == "regular":
        data_schedule = load_user_data()
    elif type_schedule == "one_time":
        data_schedule = load_one_time_events()

    count = 0 # переменная для хранения номера события

    for i in range(len(data_schedule[user_id])): # перебор всех дней недели
        for j in range(len(data_schedule[user_id][i])): # перебор всех событий
            count += 1 # увеличить номер события на 1
            if count == number_schedule: # если номер события равен искомому
                return i,j # вернуть индекс дня недели и номер события
            else: # если номер события не равен искомому, то продолжить цикл
                continue
            return False # если событие не найдено, вернуть False
# ==================================================================================== #


# ======================== ЗАПОЛНЕНИЕ СПИСКА ВСЕМИ СОБЫТИЯМИ ================================
data_ivent = [] # список для хранения всех событий
def get_ivent(on_time):
    if on_time == True: # если нужно получить все еженедельные события
        data_schedule = load_user_data()
    else: # если нужно получить все разовые события
        data_schedule = load_one_time_events()
    # ---------------------- перебор всех событий -------------------------------
    for key, item in data_schedule.items(): # перебор всех пользователей
        for iter_schedule in item: # перебор всех дней недели
            for iter_weekday in iter_schedule: # перебор всех событий
                # добавление в список всех событий с указанием дня недели, времени и события
                data_ivent.append([key, iter_weekday.get("WeekDay"), iter_weekday.get('Time'), iter_weekday.get('Event'), iter_weekday.get('time_before')])
# ==================================================================================== #


# ======================== ОТПРАВКА НАПОМИНАНИЙ ================================
def send_reminders():
    while True:
        get_ivent(False) # получить все разовые события
        get_ivent(True) # получить все еженедельные события
        for ivent in data_ivent: # перебор всех событий
            if ivent[1] == time.strftime("%A") and ivent[2] == time.strftime("%H:%M") \
                or ivent[1] == time.strftime("%A") and ivent[2] == time.strftime("%H:%M", time.localtime(time.time() + int(ivent[4]) * 60)): # если день недели и время совпадает с текущим
                lang = load_data_user()[str(ivent[0])]["lang"] # загрузить данные и получить язык пользователя
                bot.send_message(int(ivent[0]), f"<b>❗️{dict_lang['Reminders'][lang]}❗️</b>\n{ivent[3]}", parse_mode="HTML")
            else: continue # продолжить цикл в случае несоответствия условию

        # ======= Очистка разовых событий ================== #
        if time.strftime("%H:%M") == "23:59":
            data_schedule_one_time = load_one_time_events()
            data_schedule_one_time = {}
            save_one_time_events(data_schedule_one_time)
        # ================================================== #
        time.sleep(30) # задержка в 30 секунд

        data_ivent.clear() # очистить список



reminder_thread = Thread(target=send_reminders) # создание потока для отправки напоминаний
reminder_thread.start() # запуск потока
# ==================================================================================== #

# ======================== ОБРАБОТЧИК РАЗОВЫХ СОБЫТИЙ ================================
@bot.message_handler(func=lambda message: message.text[0] == "!" or message.text[0] == "*", content_types=['text'])
def handle_enter_event(message):
    one_time_events = load_one_time_events()
    lang = load_data_user()[str(message.chat.id)]["lang"] # загрузить данные и получить язык пользователя
    if len(message.text[1:].split(" ")) > 1: # если введено больше двух значение (время и событие)

        if int(message.text[1:6].split(":")[0]) < 23 or int(message.text[1:6].split(":")[1]) < 59:  # если время введено некорректно

            if str(message.chat.id) not in one_time_events:
                one_time_events[str(message.chat.id)] = [[]]
                one_time_events[str(message.chat.id)][0].append({"WeekDay":  time.strftime("%A"), "Time": message.text[1:].split(" ")[0],
                                                        "Event": " ".join(message.text.split(" ")[1:]),"time_before":"0"})
            else:
                one_time_events[str(message.chat.id)][0].append({"WeekDay":  time.strftime("%A"), "Time": message.text[1:].split(" ")[0],
                                                        "Event": " ".join(message.text.split(" ")[1:]),"time_before":"0"})

            save_one_time_events(one_time_events)

            bot.send_message(message.chat.id, dict_lang["Saving_OT_event"][lang])
        else:
            bot.send_message(message.chat.id, dict_lang["Incorrect_time"][lang])
    else:
        bot.send_message(message.chat.id, dict_lang["Incorrect_enter_for_one_time_event"][lang])
# ==================================================================================== #

# ========================== ОБРАБОТЧИК ГОЛОСОВЫХ СООБЩЕНИЙ ====================================
@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    lang = load_data_user()[str(message.chat.id)]["lang"] # загрузить данные и получить язык пользователя
    global number_dict # глобальная переменная для хранения словаря с числами
    answer_message = bot.send_message(message.chat.id, dict_lang["Waiting_processing"][lang]) # отправить сообщение с текстом об ожидание
    file_info = bot.get_file(message.voice.file_id) # получить информацию о файле голосового сообщения
    downloaded_file = bot.download_file(file_info.file_path) # скачать файл голосового сообщения
    with open('new_file.ogg', 'wb') as new_file: # создать файл с названием new_file.ogg
        new_file.write(downloaded_file) # записать в файл голосовое сообщение

        # Работа с API AssemblyAI для распознавания голосового сообщения
        aai.settings.api_key = f"TOKEN"

        FILE_URL = 'new_file.ogg' # путь к файлу
        config = aai.TranscriptionConfig(language_code="ru") # язык распознавания голосового сообщения

        transcriber = aai.Transcriber(config=config) # создание объекта для распознавания голосового сообщения
        transcript = transcriber.transcribe(FILE_URL) # распознавание голосового сообщения и запись в переменную transcript

        text_voice = transcript.text.lower().split(" ") # разделить распознанный текст на слова

        # ------- удаление знаков препинания --------------
        for i in range(len(text_voice)):
            text_voice[i] = text_voice[i].replace(',', '')
            text_voice[i] = text_voice[i].replace('.', '')
            text_voice[i] = text_voice[i].replace('-', '')
        # -------------------------------------------------

        # ------- поиск дня недели в распознанном тексте --------------
        try: # если день недели найден в распознанном тексте - значит это еженедельное событие
            week_day_en = [day[1] for day in days_of_week if day[0].lower() == text_voice[0]][0]
            type_ivent = "every_week"
        except: # если день недели не найден в распознанном тексте - значит это разовое событие
            week_day_en = "Разовое событие"
            type_ivent = "one_time"
        # -------------------------------------------------------------


        time_ivent, index_word = "", 0 # переменная для хранения времени и индекса слова в распознанном тексте
        index_word = 1 if type_ivent == "every_week" else 0 # если еженедельное событие, индекс слова равен 1, иначе 0

        # --------------цикл для получения времени из распознанного текста --------------------
        last_symb = 0 # переменная для хранения последнего символа

        for word in text_voice[index_word:]: # перебор слов в распознанном тексте
            if len(time_ivent) == 2: # если в переменной time_ivent 2 символа
                time_ivent += ":" # добавить двоеточие

            if len(time_ivent) == 5: # если в переменной time_ivent 5 символов ( польностью введено время)
                if number_dict.get(word.lower()) != None: # если следующее слово является числом
                    time_ivent = time_ivent[:-1] + str(number_dict.get(word.lower())) # заменить последний символ на число
                    last_symb = 1 # установить значение на 1

                index_word = text_voice.index(word) + last_symb # получить индекс слова в распознанном тексте
                break # выйти из цикла

            if number_dict.get(word.lower()) != None: # если слово является числом
                time_ivent += str(number_dict.get(word.lower())) # добавить число в переменную time_ivent
            try: # если значение является числом в виде строки
                if int(word): time_ivent = f'{word[0:2]}:{word[2:4]}' # добавить в переменную time_ivent время
            except: continue # продолжить цикл в случае несоответствия условию
        # ------------------------------------------------------------------------------------- #

        text_voice_ivent = " ".join(text_voice[index_word:]) # объединить слова в распознанном тексте в одну строку
        try: # если день недели найден в распознанном тексте
            week_day_ivent = dict_lang[week_day_en][lang]
        except: # если день недели не найден в распознанном тексте
            week_day_ivent = dict_lang["One_time_event"][lang]

        # Проверить, введено ли время корректно (HH:MM)
        if len(time_ivent) != 5: # если время введено некорректно
            bot.edit_message_text(chat_id=message.chat.id, message_id=answer_message.message_id, text=dict_lang["Incorrect_time"][lang]) # отправить сообщение с ошибкой
            time_ivent = "" # обнулить время
        else:
            # вывод итог для уточнения у пользователя
            output = f'<b>|{week_day_ivent}| <u>|{time_ivent}|</u> |{text_voice_ivent}|</b>' # объединить день недели, время и событие в одну строку

            # очищаю список от предыдущих значений и добавляю новые значения, являющие день недели, время и событие
            ivent_user_voice.clear(); ivent_user_voice.extend([week_day_en, time_ivent, text_voice_ivent])
            # необходимы для сохранения события в файле и вывода итога для уточнения у пользователя

            # отредактировать отправленное сообщение с текстом с созданием кнопок "Сохранить" и "Отмена"
            keyboard = types.InlineKeyboardMarkup()
            buttonSave = types.InlineKeyboardButton(text=dict_lang["button_save"][lang], callback_data="callback_save_voice")
            buttonCancel = types.InlineKeyboardButton(text=dict_lang["button_cancel"][lang], callback_data="callback_cancel_voice")
            keyboard.add(buttonSave,buttonCancel)
            bot.edit_message_text(chat_id=message.chat.id, message_id=answer_message.message_id, text=f'{dict_lang["Question_correct_event"][lang]}\n {output}', reply_markup=keyboard, parse_mode='html')
            # при callback нажатии на кнопку сохранить или отмена будет вызван обработчик callback кнопок



if __name__ == "__main__":
    print("Бот запущен!")
    # запустить бота чтоб он работал постоянно
    bot.polling(none_stop=True, interval=0, timeout=0)
