const { Client, GatewayIntentBits, Events } = require('discord.js');
const fs = require('fs');

const DATA_FILE = 'messages.json';

function loadMessages() {
  if (!fs.existsSync(DATA_FILE)) return {};
  return JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
}

function saveMessages(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf-8');
}

const client = new Client({
  intents: [
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.MessageContent,
  ],
});

client.once(Events.ClientReady, (c) => {
  console.log(`봇 로그인 완료: ${c.user.tag}`);
});

client.on(Events.MessageCreate, async (message) => {
  if (message.author.bot) return;
  if (message.channel.type !== 1) return; // 1 = DMChannel

  const userId = message.author.id;
  const text = message.content;
  const timestamp = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

  if (text === '!help') {
    return message.reply(
      '📌 **메시지 저장 봇 사용법**\n\n' +
      '봇에게 **DM**으로 메시지를 보내면 자동으로 저장됩니다.\n\n' +
      '**명령어:**\n' +
      '`!list` — 저장된 메시지 목록 보기\n' +
      '`!clear` — 저장된 메시지 모두 삭제\n' +
      '`!help` — 도움말'
    );
  }

  if (text === '!list') {
    const data = loadMessages();
    const messages = data[userId] ?? [];
    if (messages.length === 0) return message.reply('저장된 메시지가 없습니다.');

    const lines = [`📋 **저장된 메시지 (${messages.length}개):**\n`];
    for (const [i, msg] of messages.entries()) {
      lines.push(`**${i + 1}.** \`${msg.time}\`\n${msg.text}\n`);
    }

    let response = lines.join('\n');
    if (response.length > 1900) response = response.slice(0, 1900) + '\n... (너무 많아 일부 생략)';
    return message.reply(response);
  }

  if (text === '!clear') {
    const data = loadMessages();
    const count = (data[userId] ?? []).length;
    data[userId] = [];
    saveMessages(data);
    return message.reply(`🗑️ ${count}개의 메시지가 삭제되었습니다.`);
  }

  // 일반 메시지 저장
  const data = loadMessages();
  if (!data[userId]) data[userId] = [];
  data[userId].push({ text, time: timestamp });
  saveMessages(data);

  await message.reply(`✅ 저장되었습니다!\n🕐 ${timestamp}`);
});

const token = process.env.DISCORD_BOT_TOKEN;
if (!token) throw new Error('DISCORD_BOT_TOKEN 환경 변수를 설정해주세요.');
client.login(token);
