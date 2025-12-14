import telebot
from telebot import types
import json
import os

TOKEN = "8281269314:AAE_rjrQdbEYWWqmv-8FKe-VHZButA00RAE"
bot = telebot.TeleBot(TOKEN)

with open("data/grenades.json", "r", encoding="utf-8") as f:
    grenades = json.load(f)

# Стартовое меню: выбор карты 
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    for map_name in grenades.keys():
        markup.add(types.InlineKeyboardButton(text=map_name.capitalize(), callback_data=f"map_{map_name}"))
    bot.send_message(message.chat.id, "Выбери карту:", reply_markup=markup)

#  Выбор стороны 
@bot.callback_query_handler(func=lambda call: call.data.startswith("map_"))
def choose_side(call):
    map_name = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("T — Террористы", callback_data=f"side_{map_name}_T"),
        types.InlineKeyboardButton("CT — Спецназ", callback_data=f"side_{map_name}_CT")
    )
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="back_main"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"Карта: {map_name.capitalize()}\nВыбери сторону:", reply_markup=markup)

#  Выбор гранаты 
@bot.callback_query_handler(func=lambda call: call.data.startswith("side_"))
def choose_grenade(call):
    _, map_name, side = call.data.split("_")
    grenades_list = grenades[map_name][side]
    markup = types.InlineKeyboardMarkup()

    for name in grenades_list.keys():
        markup.add(types.InlineKeyboardButton(
            text=name.replace("_", " ").capitalize(),
            callback_data=f"grenade_{map_name}_{side}_{name}"
        ))
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data=f"map_{map_name}"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f"{map_name.capitalize()} ({side}) — выбери гранату:",
                          reply_markup=markup)

#  Отправка информации по гранате 
@bot.callback_query_handler(func=lambda call: call.data.startswith("grenade_"))
def show_grenade(call):
    _, map_name, side, name = call.data.split("_", 3)
    g = grenades[map_name][side][name]

    # Фото
    if "photo" in g and os.path.exists(g["photo"]):
        with open(g["photo"], "rb") as img:
            bot.send_photo(call.message.chat.id, img, caption=f"{map_name.capitalize()} ({side}) — {name.replace('_', ' ').capitalize()}")

    # Текст
    if "instruction" in g:
        bot.send_message(call.message.chat.id, f"Как бросить:\n{g['instruction']}")

    # Видео
    if "video" in g and os.path.exists(g["video"]):
        with open(g["video"], "rb") as vid:
            bot.send_video(call.message.chat.id, vid, caption="Пример выполнения.")
    else:
        bot.send_message(call.message.chat.id, "Видео не найдено.")

#  Кнопка "Назад" 
@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back(call):
    markup = types.InlineKeyboardMarkup()
    for map_name in grenades.keys():
        markup.add(types.InlineKeyboardButton(text=map_name.capitalize(), callback_data=f"map_{map_name}"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text="Выбери карту:", reply_markup=markup)

bot.polling()
