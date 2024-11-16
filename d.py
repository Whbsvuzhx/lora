import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Set your bot token and admin user ID
BOT_TOKEN = '7329014487:AAFWyiXtttJU-QXkfQ8CsWoHiJhpQ44oubo'
ADMIN_USER_ID = 5163805719  # Replace with your Telegram user ID

# Store approved users (this could be a file or database in production)
approved_users = set()

# Payload management functions
def generate_payload(length=1024):
    """Generate a random payload (byte array) of a given length."""
    return [random.randint(0, 255) for _ in range(length)]

def generate_unique_payloads(num_payloads):
    """Generate a set of unique random payloads, each 1024 bytes long."""
    unique_payloads = set()
    while len(unique_payloads) < num_payloads:
        payload = tuple(generate_payload())
        unique_payloads.add(payload)
    return list(unique_payloads)

def format_payload(payload):
    """Format a single payload as a C-style byte array."""
    return '{' + ', '.join(f'0x{byte:02x}' for byte in payload) + '}'

# Telegram bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message."""
    await update.message.reply_text("Welcome to the Payload Generator Bot! Use /generate <number> to create payloads.")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate payloads and send them directly to the user if they are approved."""
    if update.effective_user.id not in approved_users:
        await update.message.reply_text("You are not approved to use this bot. Please contact the admin.")
        return

    # Parse the number of payloads from the command arguments
    try:
        num_payloads = int(context.args[0])
        if num_payloads < 1:
            raise ValueError("Number must be positive.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /generate <number_of_payloads>")
        return

    # Generate unique payloads
    payloads = generate_unique_payloads(num_payloads)
    
    # Format the payloads as a string (chunk them if too long)
    formatted_payloads = [format_payload(payload) for payload in payloads]
    response = "\n\n".join(formatted_payloads)

    # Telegram message has a character limit (4096). If it's too long, send in chunks.
    chunk_size = 4096
    for i in range(0, len(response), chunk_size):
        await update.message.reply_text(response[i:i+chunk_size])

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a user to use the bot."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("Access denied. Admins only.")
        return

    # Get the user ID to approve
    try:
        user_id = int(context.args[0])
        approved_users.add(user_id)
        await update.message.reply_text(f"User {user_id} has been approved to use the bot.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /approve <user_id>")

async def disapprove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disapprove a user from using the bot."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("Access denied. Admins only.")
        return

    # Get the user ID to disapprove
    try:
        user_id = int(context.args[0])
        if user_id in approved_users:
            approved_users.remove(user_id)
            await update.message.reply_text(f"User {user_id} has been disapproved from using the bot.")
        else:
            await update.message.reply_text(f"User {user_id} is not approved.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /disapprove <user_id>")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help information."""
    help_text = (
        "/start - Welcome message\n"
        "/generate <number> - Generate unique payloads\n"
        "/approve <user_id> - Approve a user to use the bot\n"
        "/disapprove <user_id> - Disapprove a user from using the bot\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

# Main bot setup
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", generate))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("disapprove", disapprove))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()