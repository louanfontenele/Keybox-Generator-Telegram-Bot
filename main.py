import logging
import os
import json
import time
from datetime import datetime, timedelta, timezone

from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
    CallbackQueryHandler,
)
from dotenv import load_dotenv
import keyboxGenerator

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Constants and Configuration ---
ADMIN_USER_ID = 5685799208  # Replace with your actual user ID
DAILY_LIMIT = 5
LIMIT_DURATION_HOURS = 24
DATA_FILE = "user_data.json"

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Data Management Functions ---

def load_data():
    """Loads user data from the JSON file."""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    """Saves user data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_data(user_id, data):
    """Gets user data, creating a default entry if needed."""
    user_id_str = str(user_id)  # Ensure string for JSON keys
    if user_id_str not in data:
        data[user_id_str] = {
            "count": 0,
            "last_reset": int(time.time()),  # Unix timestamp
            "vip": False
        }
    return data[user_id_str]


def check_and_reset_limit(user_data):
    """Checks if the time limit has expired and resets the count if needed."""

    current_time = int(time.time())
    last_reset_time = user_data["last_reset"]

    if current_time - last_reset_time >= LIMIT_DURATION_HOURS * 3600:
        user_data["count"] = 0
        user_data["last_reset"] = current_time
        return True # indicates limit has reset
    return False


def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for MarkdownV2."""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(("\\" + char if char in escape_chars else char) for char in text)

# --- Telegram Bot Handlers ---

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Generate Keybox", callback_data="generate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"Hi {user.first_name}! 👋\n\n"
        "Welcome to the Keybox Generator Bot! I can create `keybox.xml` files "
        "used for Android device attestation.\n\n"
        "Click the button below to get started, or use /help for more information."
    )

    await update.message.reply_text(
        escape_markdown_v2(message), reply_markup=reply_markup, parse_mode="MarkdownV2"
    )


async def generate_keybox_command(update: Update, context: CallbackContext) -> None:
    """Generates the keybox and sends it, checking limits."""
    query = update.callback_query
    user_id = update.effective_user.id

    # Load data, get user, check/reset limit, check vip
    data = load_data()
    user_data = get_user_data(user_id, data)
    limit_reset = check_and_reset_limit(user_data)


    if user_data["vip"]:
      limit_message = "👑 You are a VIP user.  Unlimited keybox generation!"

    elif user_data["count"] >= DAILY_LIMIT:
       # Calculate remaining time
        current_time = int(time.time())
        last_reset_time = user_data["last_reset"]
        time_remaining_seconds = LIMIT_DURATION_HOURS * 3600 - (current_time - last_reset_time)
        time_remaining = timedelta(seconds = time_remaining_seconds)

        limit_message = (
            f"❌ You have reached your daily limit of {DAILY_LIMIT} keyboxes.\n"
            f"Time remaining until reset: {time_remaining}"
        )
        if query:
            await query.answer()
            await query.edit_message_text(escape_markdown_v2(limit_message))
        else:
            await update.message.reply_text(escape_markdown_v2(limit_message))
        return  # Stop here if the limit is reached

    else:

      limit_message = f"🔑 Keyboxes generated today: {user_data['count']}/{DAILY_LIMIT}"
      if(limit_reset):
          limit_message = f"✅ Your daily Keybox limit has been reset\n{limit_message}"
    # Proceed with keybox generation
    if query:
        await query.answer()  # Always answer!
        await query.edit_message_text(text=f"Generating keybox.xml...\n{limit_message}")
    else:
        await update.message.reply_text(f"Generating keybox.xml...\n{limit_message}")

    result = keyboxGenerator.main()

    if result.startswith("Successfully"):
        user_data["count"] += 1  # Increment count
        save_data(data)  # Save the updated count *before* sending
        with open("keybox.xml", "rb") as f:
            if query:
                await query.message.reply_document(document=f, filename="keybox.xml")
            else:
                await update.message.reply_document(document=f, filename="keybox.xml")

        # Success message with options
        keyboard = [
            [InlineKeyboardButton("Generate Another Keybox", callback_data="generate")],
            [InlineKeyboardButton("Show Help", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        success_message = f"✅ Keybox generated successfully!\n{limit_message}\nWhat would you like to do next?"

        if query:
            await query.message.reply_text(
                escape_markdown_v2(success_message), reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                escape_markdown_v2(success_message), reply_markup=reply_markup
            )
    elif "keybox" in result.lower() and "</" in result.lower():
         user_data["count"] += 1  # Increment count
         save_data(data)
         if query:
             await query.message.reply_text(f"Generated keybox (sent as text):\n{limit_message}")
             await query.message.reply_text(
                f"Generated Keybox:\n```{escape_markdown_v2(result)}```", parse_mode="MarkdownV2"
             )
         else:

             await update.message.reply_text(f"Generated keybox (sent as text):\n{limit_message}")
             await update.message.reply_text(
               f"Generated Keybox:\n```{escape_markdown_v2(result)}```", parse_mode="MarkdownV2"
           )

         # Success message with options
         keyboard = [
            [InlineKeyboardButton("Generate Another Keybox", callback_data="generate")],
            [InlineKeyboardButton("Show Help", callback_data="help")],
        ]
         reply_markup = InlineKeyboardMarkup(keyboard)
         success_message = "✅ Keybox generated successfully! What would you like to do next?"

         if query:

            await query.message.reply_text(escape_markdown_v2(success_message), reply_markup=reply_markup)
         else:
             await update.message.reply_text(escape_markdown_v2(success_message), reply_markup=reply_markup)
    else:
        if query:
            await query.message.reply_text(escape_markdown_v2(result))  # Escape error
        else:
            await update.message.reply_text(escape_markdown_v2(result))

async def help_command(update: Update, context: CallbackContext) -> None:
    """Shows the help message."""
    keyboard = [
        [
            InlineKeyboardButton(
                "View Source Code (GitHub)",
                url="https://github.com/CRZX1337/Keybox-Generator-Telegram-Bot",
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        "This bot generates Android keybox.xml files.\n\n"
        "**Commands:**\n\n"
        "/start - Start the bot and see the welcome message.\n"
        "/generate - Create a new keybox.xml file.\n"
        "/help - Show this help message.\n\n"
        "Click the button below to view the source code on GitHub."
    )

    query = update.callback_query
    if query:
         await query.answer()
         await query.edit_message_text(
            escape_markdown_v2(message), reply_markup=reply_markup, parse_mode="MarkdownV2"
        )
    else:
        await update.message.reply_text(
            escape_markdown_v2(message), reply_markup=reply_markup, parse_mode="MarkdownV2"
        )




async def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    if query.data == "generate":
        await generate_keybox_command(update, context)
    elif query.data == "help":
        await help_command(update, context)
    else:
        await query.edit_message_text(text=f"Selected option: {query.data}")



# --- Admin Commands ---

async def admin_panel(update: Update, context: CallbackContext) -> None:
    """Displays the admin panel."""
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Unauthorized.")
        return

    keyboard = [
        [InlineKeyboardButton("List Users", callback_data="admin_list")],
        [InlineKeyboardButton("Add VIP", callback_data="admin_add_vip")],
        [InlineKeyboardButton("Remove VIP", callback_data="admin_remove_vip")],
        [InlineKeyboardButton("Show Limit", callback_data="admin_show_limit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin Panel:", reply_markup=reply_markup)


async def admin_list_users(update: Update, context: CallbackContext) -> None:
     """Lists all users and their data (admin only)."""
     query = update.callback_query
     await query.answer()

     if query.from_user.id != ADMIN_USER_ID:
         await query.edit_message_text("Unauthorized.")
         return
     data = load_data()

     if not data:
          await query.edit_message_text("No user data found.")
          return
     user_list = ""

     for user_id, user_data in data.items():
        user_list += (
             f"ID: {user_id}, Count: {user_data['count']}, "
             f"Last Reset: {datetime.fromtimestamp(user_data['last_reset'])}, VIP: {user_data['vip']}\n"
        )
     await query.edit_message_text(f"User List:\n{user_list}")

async def admin_add_vip(update: Update, context: CallbackContext) -> None:
    """Adds a VIP user (admin only)."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_USER_ID:
         await query.edit_message_text("Unauthorized.")
         return

    await query.edit_message_text("Enter the User ID to add as VIP:")
    context.user_data["admin_action"] = "add_vip"


async def admin_remove_vip(update: Update, context: CallbackContext) -> None:
    """Removes a VIP user (admin only)."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_USER_ID:
         await query.edit_message_text("Unauthorized.")
         return
    await query.edit_message_text("Enter the User ID to remove from VIP:")
    context.user_data["admin_action"] = "remove_vip"

async def admin_show_limit(update: Update, context: CallbackContext) -> None:
    """Removes a VIP user (admin only)."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_USER_ID:
         await query.edit_message_text("Unauthorized.")
         return
    message = f"The current limits are:\n-Limit: {DAILY_LIMIT}\n-Duration: {LIMIT_DURATION_HOURS} hours"
    await query.edit_message_text(message)

async def handle_admin_input(update: Update, context: CallbackContext) -> None:
    """Handles input for admin commands (e.g., adding/removing VIPs)."""
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Unauthorized.")
        return

    if "admin_action" not in context.user_data:
        # Not in an admin action flow, just ignore.
        return


    text = update.message.text
    admin_action = context.user_data.pop("admin_action") # Remove after use

    if admin_action == "add_vip":
        try:
             vip_user_id = int(text)
             data = load_data()
             user_data = get_user_data(vip_user_id,data) # creates if doesn exist
             user_data["vip"] = True
             save_data(data)
             await update.message.reply_text(f"User {vip_user_id} added to VIPs.")

        except ValueError:
            await update.message.reply_text("Invalid User ID format.")

    elif admin_action == "remove_vip":
        try:
           vip_user_id = int(text)
           data = load_data()
           if str(vip_user_id) not in data:
                await update.message.reply_text("User Id not found")
                return
           data[str(vip_user_id)]["vip"] = False
           save_data(data)
           await update.message.reply_text(f"User {vip_user_id} removed from VIPs.")

        except ValueError:
            await update.message.reply_text("Invalid User ID format.")



async def admin_button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_USER_ID:
        await query.edit_message_text("Unauthorized.")
        return

    if query.data == "admin_list":
        await admin_list_users(update, context)
    elif query.data == "admin_add_vip":
        await admin_add_vip(update, context)
    elif query.data == "admin_remove_vip":
       await admin_remove_vip(update, context)
    elif query.data == "admin_show_limit":
        await admin_show_limit(update, context)
    else:
      await query.edit_message_text(text=f"Selected option: {query.data}")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate_keybox_command))
    application.add_handler(CommandHandler("admin", admin_panel)) # admin panel
    application.add_handler(CallbackQueryHandler(button, pattern='^(?!admin_)')) # Handles buttons except "admin_"
    application.add_handler(CallbackQueryHandler(admin_button, pattern='^admin_')) # Handle admin panel buttons
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_input)) # get input

    application.run_polling()


if __name__ == "__main__":
    main()