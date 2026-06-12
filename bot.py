import os
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DATA_FILE = "messages.json"


def load_messages() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_messages(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "안녕하세요! 메시지 저장 봇입니다.\n\n"
        "📌 사용법:\n"
        "• 메시지를 보내면 자동으로 저장됩니다.\n"
        "• /list — 저장된 메시지 목록 보기\n"
        "• /clear — 저장된 메시지 모두 삭제\n"
        "• /help — 도움말"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📌 명령어 목록:\n\n"
        "/start — 시작\n"
        "/list — 저장된 메시지 보기\n"
        "/clear — 모든 메시지 삭제\n"
        "/help — 도움말\n\n"
        "메시지를 입력하면 날짜/시간과 함께 저장됩니다."
    )


async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    text = update.message.text
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = load_messages()
    if user_id not in data:
        data[user_id] = []

    data[user_id].append({"text": text, "time": timestamp})
    save_messages(data)

    await update.message.reply_text(f"✅ 저장되었습니다!\n🕐 {timestamp}")


async def list_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    data = load_messages()
    messages = data.get(user_id, [])

    if not messages:
        await update.message.reply_text("저장된 메시지가 없습니다.")
        return

    lines = [f"📋 저장된 메시지 ({len(messages)}개):\n"]
    for i, msg in enumerate(messages, 1):
        lines.append(f"{i}. [{msg['time']}]\n{msg['text']}\n")

    # Telegram message limit: 4096 chars
    response = "\n".join(lines)
    if len(response) > 4000:
        response = response[:4000] + "\n... (너무 많아 일부 생략)"

    await update.message.reply_text(response)


async def clear_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    data = load_messages()
    count = len(data.get(user_id, []))
    data[user_id] = []
    save_messages(data)

    await update.message.reply_text(f"🗑️ {count}개의 메시지가 삭제되었습니다.")


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN 환경 변수를 설정해주세요.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_messages))
    app.add_handler(CommandHandler("clear", clear_messages))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))

    logger.info("봇이 시작되었습니다...")
    app.run_polling()


if __name__ == "__main__":
    main()
