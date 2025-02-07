import logging
import os
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

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for MarkdownV2."""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(("\\" + char if char in escape_chars else char) for char in text)

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Generate Keybox", callback_data="generate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"Hi {user.first_name}! 👋\n\n"
        "Welcome to the Keybox Generator Bot!  I can create `keybox.xml` files "
        "used for Android device attestation.\n\n"
        "Click the button below to get started, or use /help for more information."
    )

    await update.message.reply_text(
        escape_markdown_v2(message), reply_markup=reply_markup, parse_mode="MarkdownV2"
    )


async def generate_keybox_command(update: Update, context: CallbackContext) -> None:
    """Generates the keybox and sends it."""
    query = update.callback_query
    if query:
        await query.answer() # Always answer callback queries!
        await query.edit_message_text(text="Generating keybox.xml...")

    else:
      await update.message.reply_text("Generating keybox.xml...")



    result = keyboxGenerator.main()
    if result.startswith("Successfully"):
        with open("keybox.xml", "rb") as f:
             if query:
                 await query.message.reply_document(document=f, filename="keybox.xml")

             else:
                 await update.message.reply_document(document=f, filename="keybox.xml")
        # Success message WITH options
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


    elif "keybox" in result.lower() and "</" in result.lower():

        if query:
            await query.message.reply_text(
                f"Generated Keybox:\n```{escape_markdown_v2(result)}```", parse_mode="MarkdownV2"
            )
        else:
            await update.message.reply_text(
               f"Generated Keybox:\n```{escape_markdown_v2(result)}```", parse_mode="MarkdownV2"
           )
        # Success message WITH options after text sent
        keyboard = [
            [InlineKeyboardButton("Generate Another Keybox", callback_data="generate")],
            [InlineKeyboardButton("Show Help", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        success_message = "✅ Keybox generated successfully! Find the content above. What would you like to do next?"

        if query:

             await query.message.reply_text(escape_markdown_v2(success_message), reply_markup=reply_markup)

        else:
            await update.message.reply_text(escape_markdown_v2(success_message), reply_markup=reply_markup)



    else:

        if query:
            await query.message.reply_text(escape_markdown_v2(result))  # Escape Error text
        else:
            await update.message.reply_text(escape_markdown_v2(result))

async def help_command(update: Update, context: CallbackContext) -> None:
    """Shows the help message."""
    keyboard = [
        [
            InlineKeyboardButton(
                "View Source Code (GitHub)", url="https://github.com/CRZX1337/Keybox-Generator-Telegram-Bot"
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
        await query.edit_message_text(escape_markdown_v2(message), reply_markup=reply_markup, parse_mode="MarkdownV2")

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
        await help_command(update, context)  # Correctly call help_command
    else:
        await query.edit_message_text(text=f"Selected option: {query.data}")



def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate_keybox_command))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == "__main__":
    main()