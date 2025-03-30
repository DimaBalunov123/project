import telebot
from telebot import types

BOT_TOKEN = "your token"
bot = telebot.TeleBot(BOT_TOKEN)

user_questions = {}
admin_mode = {}
faq = {
    "1": 'Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку "Добавить в корзину", затем перейдите в корзину и следуйте инструкциям для завершения покупки.',
    "2": 'Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел "Мои заказы". Там будет указан текущий статус вашего заказа.',
    "3": 'Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки.',
    "4": 'При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара.',
    "5": 'Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота.',
    "6": 'Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки.',
}


rmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("Задать вопрос")
item2 = types.KeyboardButton("Часто задаваемые вопросы")
rmarkup.add(item1, item2)


markup = types.InlineKeyboardMarkup()
button1 = types.InlineKeyboardButton("Кнопка 1", callback_data='button1_ready')
button2 = types.InlineKeyboardButton("Кнопка 2", callback_data='button2_ready')
markup.add(button1, button2)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Привет, мы интернет-магазин "Продаем все на свете!"', reply_markup=rmarkup)


@bot.message_handler(func=lambda message: message.text == 'Задать вопрос')
def user_question(message):
    bot.send_message(message.chat.id, "Задайте ваш вопрос:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_question)


def process_question(message):
    user_questions[message.from_user.id] = (message.text, False)
    bot.send_message(message.chat.id, "Вопрос отправлен.", reply_markup=rmarkup)
    notification_admin(message)


def notification_admin(message):
    for admin_id in admin_mode:
        bot.send_message(admin_id, f"Новый вопрос от {message.from_user.id}:\n{message.text}")


@bot.message_handler(commands=['admin'])
def admin_func(message):
    if message.from_user.id not in admin_mode:
        admin_mode[message.from_user.id] = True
        bot.send_message(message.chat.id, "Вы вошли в режим админа. спользуйте /admin снова, чтобы выйти", reply_markup=types.ReplyKeyboardRemove())
        for user_id, (question, admin_responded) in user_questions.items():
            if not admin_responded:
                bot.send_message(message.chat.id, f"Вопрос от {user_id}:\n{question}\n \nВведите ответ на него:")
    else:
        del admin_mode[message.from_user.id]
        bot.send_message(message.chat.id, "Вы вышли из режима администратора.", reply_markup=rmarkup)


@bot.message_handler(func=lambda message: message.text and message.chat.id in admin_mode)
def send_answer(message):
    for user_id, (question, admin_responded) in list(user_questions.items()):
        if not admin_responded:
            bot.send_message(user_id, f"Ответ: {message.text}")
            user_questions[user_id] = (question, True)
            break


@bot.message_handler(func=lambda message: message.text == "Часто задаваемые вопросы")
def faq_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for question in faq:
        button = types.InlineKeyboardButton(text=question, callback_data=question)
        markup.add(button)


    bot.send_message(message.chat.id, "Список вопросов:\n"
    "1) Как оформить заказ?\n"
    "2) Как узнать статус моего заказа?\n"
    "3) Как отменить заказ?\n"
    "4) Что делать, если товар пришел поврежденным?\n"
    "5) Как связаться с вашей технической поддержкой?\n"
    "6) Как узнать информацию о доставке?\n"
    "\nНажмите на цифру вашего вопроса", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def faq_back(call):
    question = call.data
    answer = faq.get(question)
     
    if answer:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, answer)
    else:
        bot.answer_callback_query(call.id, text="Ответ на этот вопрос не найден.")



bot.polling(none_stop=True)
