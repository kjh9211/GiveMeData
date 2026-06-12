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

  // 메시지 저장
  const data = loadMessages();
  if (!data[userId]) data[userId] = [];
  data[userId].push({ text, time: timestamp });
  saveMessages(data);

  await message.reply(`✅ 저장되었습니다!\n🕐 ${timestamp}`);
});

const token = process.env.DISCORD_BOT_TOKEN;
if (!token) throw new Error('DISCORD_BOT_TOKEN 환경 변수를 설정해주세요.');
client.login(token);
