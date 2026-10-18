#!/usr/bin/env python3
"""
Simple Telegram Bot using requests
Single file bot with HTTP requests
Author: Bot_Proxy from Hermes Agent
Date: 18.10.2026
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Создание рабочих директорий
WORKING_DIR = './telegram-working'
Path(WORKING_DIR).mkdir(parents=True, exist_ok=True)

# Конфигурация
BOT_TOKEN = '8737491152:AAFL_BSsUG1Q2nDLPfSu0-KgTPX0cXyW1EQ'
USER_ID = 128382766
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    def __init__(self):
        self.setup_handlers()
        logger.info("Simple Telegram Bot initialized")
    
    def make_api_request(self, method, params=None):
        """Отправка запросов к Telegram API"""
        try:
            import requests
            url = f"{API_URL}/{method}"
            response = requests.post(url, json=params, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def setup_handlers(self):
        """Настройка обработчиков сообщений"""
        
        def send_message(chat_id, text, reply_to_message_id=None):
            """Отправка сообщения"""
            params = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            if reply_to_message_id:
                params['reply_to_message_id'] = reply_to_message_id
            
            result = self.make_api_request('sendMessage', params)
            if result and result.get('ok'):
                logger.info(f"Message sent to {chat_id}")
                return True
            else:
                logger.error(f"Failed to send message: {result}")
                return False
        
        def handle_message(message_data):
            """Обработка входящего сообщения"""
            try:
                chat_id = message_data['message']['chat']['id']
                text = message_data['message']['text']
                message_id = message_data['message']['message_id']
                from_user = message_data['message']['from']
                
                # Проверка пользователя
                if chat_id != USER_ID:
                    send_message(chat_id, "❌ Доступ запрещен")
                    return
                
                logger.info(f"Received message from user {USER_ID}: {text}")
                
                # Отправка подтверждения
                confirmation_text = (
                    f"✅ <b>ПОДТВЕРЖДЕНИЕ</b> ✅\n\n"
                    f"📨 Ваше сообщение получено серверным ботом!\n\n"
                    f"Текст: <i>{text}</i>\n"
                    f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
                    f"🎯 Если вы это видите - бот работает идеально!"
                )
                
                if send_message(chat_id, confirmation_text, message_id):
                    logger.info("Confirmation sent to user")
                    
                    # Сохраняем сообщение в файл
                    message_info = {
                        "id": int(time.time()),
                        "type": "telegram_incoming_message",
                        "action": "process_and_reply",
                        "data": {
                            "chat_id": USER_ID,
                            "reply_to_message_id": message_id,
                            "from_username": from_user.get('username', 'unknown'),
                            "from_name": from_user.get('first_name', 'Unknown User'),
                            "received_text": text,
                            "received_at": datetime.now().isoformat(),
                            "server_bot_status": "active"
                        },
                        "status": "received",
                        "processed": False
                    }
                    
                    # Сохраняем в рабочий каталог
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_file = os.path.join(WORKING_DIR, f"server_message_{timestamp}.json")
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(message_info, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"Message saved to: {output_file}")
                else:
                    logger.error("Failed to send confirmation")
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
                # Сохраняем ошибку в файл
                error_info = {
                    "id": int(time.time()),
                    "type": "telegram_incoming_message",
                    "action": "process_and_reply",
                    "data": {
                        "chat_id": USER_ID,
                        "reply_to_message_id": message_data['message']['message_id'],
                        "from_username": message_data['message']['from'].get('username', 'unknown'),
                        "from_name": message_data['message']['from'].get('first_name', 'Unknown User'),
                        "received_text": message_data['message']['text'],
                        "received_at": datetime.now().isoformat(),
                        "server_bot_status": "error",
                        "error_message": str(e)
                    },
                    "status": "error",
                    "processed": False
                }
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                error_file = os.path.join(WORKING_DIR, f"server_message_error_{timestamp}.json")
                
                with open(error_file, 'w', encoding='utf-8') as f:
                    json.dump(error_info, f, ensure_ascii=False, indent=2)
                
                logger.error(f"Error saved to: {error_file}")
                
                # Отправка сообщения об ошибке
                error_response = (
                    f"⚠️ <b>ОШИБКА ОБРАБОТКИ</b> ⚠️\n\n"
                    f"Ваше сообщение получено, но возникла ошибка:\n"
                    f"<code>{str(e)}</code>\n\n"
                    f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                    f"🔧 Бот работает, но требует внимания"
                )
                send_message(chat_id, error_response, message_id)
        
        # Команды
        def handle_command(command, message_data):
            """Обработка команд"""
            chat_id = message_data['message']['chat']['id']
            message_id = message_data['message']['message_id']
            
            if chat_id != USER_ID:
                send_message(chat_id, "❌ Доступ запрещен")
                return
            
            if command == '/start':
                response_text = (
                    f"👋 Привет, {message_data['message']['from']['first_name']}!\n\n"
                    f"🚀 <b>HERMES AGENT TELEGRAM BOT</b>\n\n"
                    f"✅ Работает на сервере\n"
                    f"📡 Готов принимать сообщения\n"
                    f"🔄 Мониторинг сети активен\n\n"
                    f"📝 Напишите любое сообщение для теста!\n\n"
                    f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                )
            elif command == '/test':
                response_text = (
                    f"🧪 <b>ТЕСТОВОЕ СООБЩЕНИЕ</b>\n\n"
                    f"✅ Бот работает на сервере!\n"
                    f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                )
            elif command == '/status':
                response_text = (
                    f"📊 <b>СТАТУС СИСТЕМЫ</b>\n\n"
                    f"✅ Бот: Запущен на сервере\n"
                    f"⏰ Время работы: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                    f"📁 Рабочая директория: {WORKING_DIR}\n\n"
                    f"🎯 Напишите сообщение для теста!"
                )
            elif command == '/help':
                response_text = (
                    f"ℹ️ <b>СПРАВОЧНИК КОМАНД</b>\n\n"
                    f"/start - Приветственное сообщение\n"
                    f"/test - Тестовое сообщение\n"
                    f"/status - Статус системы\n"
                    f"/help - Эта справка\n\n"
                    f"🔧 Бот передает все сообщения в Hermes Agent через файловую систему."
                )
            else:
                response_text = "❌ Неизвестная команда"
            
            send_message(chat_id, response_text, message_id)
        
        # Главный обработчик
        def update_handler(update_data):
            """Обработка обновлений от Telegram"""
            if 'message' in update_data:
                message = update_data['message']
                text = message.get('text', '')
                
                if text.startswith('/'):
                    # Команда
                    command = text.split()[0]
                    handle_command(command, update_data)
                else:
                    # Обычное сообщение
                    handle_message(update_data)
        
        # Сохраняем обработчик
        self.update_handler = update_handler
        self.send_message = send_message
    
    def send_welcome_message(self):
        """Отправка приветственного сообщения пользователю"""
        try:
            welcome_text = (
                f"🚀 <b>BOTPROXY СЕРВЕР ЗАПУЩЕН!</b> 🚀\n\n"
                f"✅ Работает на сервере\n"
                f"📡 Готов принимать ваши сообщения\n\n"
                f"👤 Пользователь: @bosdima\n"
                f"🤖 Бот: @AiDSeek_bot\n"
                f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
                f"🎯 Отправьте любое сообщение для тесте!"
            )
            
            result = self.make_api_request('sendMessage', {
                'chat_id': USER_ID,
                'text': welcome_text,
                'parse_mode': 'HTML'
            })
            
            if result and result.get('ok'):
                logger.info("Welcome message sent to user")
                return True
            else:
                logger.error(f"Failed to send welcome message: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
            return False
    
    def run(self):
        """Запуск бота"""
        try:
            logger.info("Starting Simple Telegram Bot...")
            logger.info(f"Bot Token: {BOT_TOKEN[:10]}...")
            logger.info(f"User ID: {USER_ID}")
            logger.info(f"Working Directory: {WORKING_DIR}")
            
            # Отправка приветственного сообщения
            self.send_welcome_message()
            
            # Основной цикл бота
            logger.info("Bot is running... Press Ctrl+C to stop")
            
            # Проверка обновлений каждые 5 секунд
            while True:
                try:
                    # Получение обновлений
                    updates = self.make_api_request('getUpdates', {
                        'timeout': 5,
                        'allowed_updates': ['message']
                    })
                    
                    if updates and updates.get('ok'):
                        for update in updates.get('result', []):
                            self.update_handler(update)
                    
                    time.sleep(5)
                    
                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(10)
                    
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    bot = SimpleTelegramBot()
    bot.run()