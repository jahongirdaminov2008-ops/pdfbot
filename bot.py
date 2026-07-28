import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, MenuButtonWebApp, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["https://quiz-webapp-4w7l.onrender.com"]  # masalan: https://sizning-app.onrender.com
PORT = int(os.environ.get("PORT", 10000))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Botimizga xush kelibsiz 👋\n\n"
        "PDF tayyorlash uchun chap tomondagi tugmani bosib "
        "saytimizga o'tishingiz mumkin."
    )


async def post_init(application: Application):
    # Chap tomondagi menyu tugmasini WebApp'ga bog'laymiz
    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Konvertor",
            web_app=WebAppInfo(url=WEBAPP_URL),
        )
    )


def run_health_server():
    # Render "Web Service" ochiq port kutadi, shuning uchun
    # oddiy HTTP server orqali health-check'ga javob beramiz
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, format, *args):
            pass

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
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
