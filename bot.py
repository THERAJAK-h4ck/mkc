import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)

# 🔥 YAHAN APNA BOT TOKEN DALEN
BOT_TOKEN = os.getenv('BOT_TOKEN', "8455342768:AAH3URoRvQJY5ySG8YEH8LO6txwMLvLk6Lw")

if BOT_TOKEN == "8455342768:AAH3URoRvQJY5ySG8YEH8LO6txwMLvLk6Lw":
    print("❌ PLEASE ADD BOT_TOKEN IN RENDER DASHBOARD!")
    exit(1)

# Channels
CHANNELS = [
    {'id': '@rajakkhan4x', 'name': 'Rajak Khan 4X', 'url': 'https://t.me/rajakkhan4x'},
    {'id': '@PromotionsOffers', 'name': 'Promotions', 'url': 'https://t.me/+eqtzUeGK774yMzQ1'},
    {'id': '@WorldMainSMMPanel', 'name': 'SMM Panel', 'url': 'https://t.me/+rL16oopNfU5iYzk9'},
    {'id': '@SMMUpdatesChannel', 'name': 'SMM Updates', 'url': 'https://t.me/+XUbztPQKGScwNGNl'}
]

# User data
user_join_status = {}

async def check_user_joined(user_id, context):
    try:
        for channel in CHANNELS:
            member = await context.bot.get_chat_member(channel['id'], user_id)
            if member.status in ['left', 'kicked']:
                return False
        return True
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    keyboard = []
    for channel in CHANNELS:
        keyboard.append([InlineKeyboardButton(f"📢 {channel['name']}", url=channel['url'])])
    keyboard.append([InlineKeyboardButton("✅ Check Join Status", callback_data='check_join')])
    
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\nJoin all channels to use the bot:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    has_joined = await check_user_joined(user_id, context)
    
    if has_joined:
        user_join_status[user_id] = True
        keyboard = [
            [KeyboardButton("📞 Search Number")],
            [KeyboardButton("ℹ️ About Bot")]
        ]
        await query.edit_message_text(
            "✅ Access granted! You can now use the bot.",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
    else:
        await query.answer("❌ Join all channels first!", show_alert=True)

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not user_join_status.get(user_id):
        await update.message.reply_text("❌ Please join all channels first! Use /start")
        return
    
    await update.message.reply_text("🔍 Send phone number to search:\n\nFormat: 91XXXXXXXXXX")

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not user_join_status.get(user_id):
        return
    
    number = update.message.text
    msg = await update.message.reply_text("🔄 Searching...")
    
    try:
        # API call
        api_url = f"https://happy-api-app.vercel.app/?num={number}"
        response = requests.get(api_url)
        data = response.json() if response.status_code == 200 else {}
        
        if data and not data.get('error'):
            info_text = f"📱 Number Info:\n\nNumber: {data.get('number', 'N/A')}\nCarrier: {data.get('carrier', 'N/A')}\nCountry: {data.get('country', 'N/A')}"
            await context.bot.edit_message_text(info_text, msg.chat_id, msg.message_id)
        else:
            await context.bot.edit_message_text("❌ No information found", msg.chat_id, msg.message_id)
            
    except Exception as e:
        await context.bot.edit_message_text("❌ Error searching number", msg.chat_id, msg.message_id)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern='check_join'))
    app.add_handler(MessageHandler(filters.Text("📞 Search Number"), handle_search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))
    
    print("🤖 Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()