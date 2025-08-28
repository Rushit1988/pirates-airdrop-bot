import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import pymongo
from uuid import uuid4

# Configuration
TOKEN = "8168452117:AAGSNXdqgHtFMtzxFoku3nG7oNTXV0dP1aA"  # Replace with your BotFather token
MONGO_URI = "mongodb+srv://rushit2013_db_user:9tuClhdDh4RaaLZp@cluster0.ilyrxnm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB Atlas connection string
TWITTER_URL = "https://x.com/PrtPirates"  # Replace with your Twitter/X account
PINNED_TWEET = "https://x.com/PrtPirates/status/1959572364569514489"  # Replace with pinned tweet URL

# MongoDB Setup
client = pymongo.MongoClient(MONGO_URI)
db = client["TelegramAirdropBot"]
users = db["users"]

# Initialize user data
def init_user(user_id, ref_id=None):
    user = users.find_one({"user_id": user_id})
    if not user:
        user_data = {
            "user_id": user_id,
            "balance": 200,  # 200 $PRT for joining
            "tasks": {"twitter_follow": False, "tweet_engage": False},
            "referral_id": str(uuid4()),  # Unique referral ID
            "referred_by": ref_id,
            "referrals": 0
        }
        users.insert_one(user_data)
        if ref_id:
            referrer = users.find_one({"referral_id": ref_id})
            if referrer:
                users.update_one({"referral_id": ref_id}, {"$inc": {"balance": 500, "referrals": 1}})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_id = context.args[0] if context.args else None
    init_user(user_id, ref_id)
    
    keyboard = [
        [InlineKeyboardButton("View Tasks", callback_data="tasks")],
        [InlineKeyboardButton("Check Balance", callback_data="balance")],
        [InlineKeyboardButton("Get Referral Link", callback_data="refer")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏴‍☠️ Ahoy Mateys! Welcome to the Pirates $PRT Airdrop! 🏴‍☠️\n"
        "You’ve earned 200 $PRT for joining! Complete tasks to earn more!",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = users.find_one({"user_id": user_id})

    if query.data == "tasks":
        keyboard = [
            [InlineKeyboardButton("Follow Twitter (200 $PRT)", url=TWITTER_URL)],
            [InlineKeyboardButton("Like, Comment, Retweet Pinned (300 $PRT)", url=PINNED_TWEET)],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "📋 Available Tasks:\n"
            "- Follow our Twitter (200 $PRT)\n"
            "- Like, comment, and retweet our pinned tweet (300 $PRT)\n"
            "Note: Task completion is manually verified later.",
            reply_markup=reply_markup
        )
    elif query.data == "balance":
        await query.message.reply_text(f"💰 Your $PRT Balance: {user['balance']}")
    elif query.data == "refer":
        ref_link = f"https://t.me/{context.bot.username}?start={user['referral_id']}"
        await query.message.reply_text(
            f"👥 Your Referral Link: {ref_link}\n"
            "Earn 500 $PRT per friend who joins!"
        )
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("View Tasks", callback_data="tasks")],
            [InlineKeyboardButton("Check Balance", callback_data="balance")],
            [InlineKeyboardButton("Get Referral Link", callback_data="refer")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🏴‍☠️ Pirates $PRT Airdrop Menu 🏴‍☠️", reply_markup=reply_markup)

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Follow Twitter (200 $PRT)", url=TWITTER_URL)],
        [InlineKeyboardButton("Like, Comment, Retweet Pinned (300 $PRT)", url=PINNED_TWEET)],
[InlineKeyboardButton("Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📋 Available Tasks:\n"
        "- Follow our Twitter (200 $PRT)\n"
        "- Like, comment, and retweet our pinned tweet (300 $PRT)\n"
        "Note: Task completion is manually verified later.",
        reply_markup=reply_markup
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})
    await update.message.reply_text(f"💰 Your $PRT Balance: {user['balance']}")

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})
    ref_link = f"https://t.me/{context.bot.username}?start={user['referral_id']}"
    await update.message.reply_text(
        f"👥 Your Referral Link: {ref_link}\n"
        "Earn 500 $PRT per friend who joins!"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = users.count_documents({})
    total_referrals = users.aggregate([{"$group": {"_id": None, "total": {"$sum": "$referrals"}}}]).next().get("total", 0)
    await update.message.reply_text(
        f"📊 Airdrop Stats:\n"
        f"Total Participants: {total_users}\n"
        f"Total Referrals: {total_referrals}"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tasks", tasks))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()