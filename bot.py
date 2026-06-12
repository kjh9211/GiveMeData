import os
import json
import logging
from datetime import datetime
import discord
from discord.ext import commands

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DATA_FILE = "messages.json"

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


def load_messages() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_messages(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@bot.event
async def on_ready():
    logger.info(f"봇 로그인 완료: {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    # DM 채널에서 보낸 메시지만 처리, 봇 메시지 무시
    if message.author.bot:
        return
    if not isinstance(message.channel, discord.DMChannel):
        return

    await bot.process_commands(message)

    # 명령어가 아닌 일반 메시지만 저장
    if message.content.startswith("!"):
        return

    user_id = str(message.author.id)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = load_messages()
    if user_id not in data:
        data[user_id] = []

    data[user_id].append({"text": message.content, "time": timestamp})
    save_messages(data)

    await message.reply(f"✅ 저장되었습니다!\n🕐 {timestamp}")


@bot.command(name="list")
async def list_messages(ctx: commands.Context):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("이 명령어는 DM에서만 사용할 수 있습니다.")
        return

    user_id = str(ctx.author.id)
    data = load_messages()
    messages = data.get(user_id, [])

    if not messages:
        await ctx.send("저장된 메시지가 없습니다.")
        return

    lines = [f"📋 저장된 메시지 ({len(messages)}개):\n"]
    for i, msg in enumerate(messages, 1):
        lines.append(f"**{i}.** `{msg['time']}`\n{msg['text']}\n")

    response = "\n".join(lines)
    # Discord message limit: 2000 chars
    if len(response) > 1900:
        response = response[:1900] + "\n... (너무 많아 일부 생략)"

    await ctx.send(response)


@bot.command(name="clear")
async def clear_messages(ctx: commands.Context):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("이 명령어는 DM에서만 사용할 수 있습니다.")
        return

    user_id = str(ctx.author.id)
    data = load_messages()
    count = len(data.get(user_id, []))
    data[user_id] = []
    save_messages(data)

    await ctx.send(f"🗑️ {count}개의 메시지가 삭제되었습니다.")


@bot.command(name="help")
async def help_command(ctx: commands.Context):
    await ctx.send(
        "📌 **메시지 저장 봇 사용법**\n\n"
        "봇에게 **DM**으로 메시지를 보내면 자동으로 저장됩니다.\n\n"
        "**명령어:**\n"
        "`!list` — 저장된 메시지 목록 보기\n"
        "`!clear` — 저장된 메시지 모두 삭제\n"
        "`!help` — 도움말"
    )


def main():
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN 환경 변수를 설정해주세요.")
    bot.run(token)


if __name__ == "__main__":
    main()
