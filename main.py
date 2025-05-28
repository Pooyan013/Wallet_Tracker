import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import TELEGRAM_TOKEN, ADMIN_ID
from db import init_db, add_wallet, get_wallets, delete_wallet

bot = telebot.TeleBot(TELEGRAM_TOKEN)
init_db()

def is_admin(message):
    return message.from_user.id in ADMIN_ID

@bot.message_handler(commands=['start'])
def start(message):
    if not is_admin(message): 
        bot.send_message(message.chat.id, "سیکتیر کن عمو")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("➕ اضافه کردن ولت", "📋 لیست ولت‌ها", "❌ حذف ولت")
    bot.send_message(message.chat.id, "سلام برادر حسین! چی میخوای انجام بدی؟", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "➕ اضافه کردن ولت")
def ask_add_wallet(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "❌ دسترسی ندارید.")
        return
    bot.send_message(message.chat.id, "آدرس ولت و اسم مستعار رو به این شکل بفرست:\n`آدرس اسم`", parse_mode="Markdown")
    bot.register_next_step_handler(message, add_wallet_handler)

def add_wallet_handler(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "سیکتیر کن عمو")
        return
    try:
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ فرمت اشتباه بود. لطفا به این شکل بفرست:\nآدرس اسم")
            return
        address, name = parts
        add_wallet(address, name)
        bot.send_message(message.chat.id, f"✅ ولت {name} با موفقیت اضافه شد.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطا در اضافه کردن ولت: {e}")

@bot.message_handler(func=lambda msg: msg.text == "📋 لیست ولت‌ها")
def show_wallets(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "سیکتیر کن عمو")
        return
    wallets = get_wallets()
    if not wallets:
        bot.send_message(message.chat.id, "⛔️ ولتی ثبت نشده.")
        return
    text = "\n".join([f"{w[1]}:\n{w[0]}" for w in wallets])
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "❌ حذف ولت")
def ask_delete_wallet(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "سیکتیر کن عمو")
        return
    wallets = get_wallets()
    if not wallets:
        bot.send_message(message.chat.id, "⛔️ ولتی برای حذف نیست.")
        return
    markup = InlineKeyboardMarkup()
    for addr, name in wallets:
        markup.add(InlineKeyboardButton(f"{name}", callback_data=f"del:{addr}"))
    bot.send_message(message.chat.id, "کدوم ولت رو حذف کنم؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del:"))
def delete_wallet_callback(call):
    if call.from_user.id not in ADMIN_ID:
        bot.answer_callback_query(call.id, "سیکتیر کن عمو")
        return
    address = call.data.split(":")[1]
    delete_wallet(address)
    bot.answer_callback_query(call.id, "🗑 حذف شد.")
    bot.edit_message_text("✅ حذف انجام شد.", call.message.chat.id, call.message.message_id)

    wallets = get_wallets()
    if wallets:
        text = "لیست ولت‌ها:\n" + "\n".join([f"{w[1]}:\n{w[0]}" for w in wallets])
    else:
        text = "ولت یخدی"
    bot.send_message(call.message.chat.id, text)

bot.infinity_polling()
