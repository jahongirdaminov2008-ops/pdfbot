import logging
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, MenuButtonWebApp, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        logger.error("Environment o'zgaruvchisi topilmadi: %s", name)
        sys.exit(1)
    return value


BOT_TOKEN = get_env("BOT_TOKEN")
WEBAPP_URL = get_env("WEBAPP_URL")  # masalan: https://sizning-app.onrender.com
PORT = int(os.environ.get("PORT", 10000))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Botimizga xush kelibsiz 👋\n\n"
        "PDF tayyorlash uchun chap tomondagi tugmani bosib "
        "saytimizga o'tishingiz mumkin."
    )


async def post_init(application: Application):
    # Agar bot oldin webhook rejimida ishlatilgan bo'lsa, uni o'chiramiz —
    # aks holda Telegram polling so'rovlariga javob bermaydi (webhook va
    # polling bir vaqtda ishlay olmaydi). Shu bilan eski navbatda qolib
    # ketgan xabarlarni ham tashlab yuboramiz.
    await application.bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook tozalandi, polling rejimiga o'tildi")

    # Chap tomondagi menyu tugmasini WebApp'ga bog'laymiz
    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Konvertor",
            web_app=WebAppInfo(url=WEBAPP_URL),
        )
    )
    logger.info("Menyu tugmasi WebApp'ga bog'landi: %s", WEBAPP_URL)


def run_health_server():
    # Render "Web Service" ochiq port kutadi, shuning uchun
    # oddiy HTTP server orqali health-check'ga javob beramiz
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, format, *args):
            pass  # standart HTTP loglarini o'chiramiz, faqat bot loglari qolsin

    logger.info("Health-check server %s portida ishga tushdi", PORT)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    application.add_handler(CommandHandler("start", start))

    logger.info("Bot polling rejimida ishga tushmoqda...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
