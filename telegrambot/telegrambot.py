from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging, os, asyncio, aiomysql, traceback, locale
import matplotlib.pyplot as plt
from io import BytesIO

token=os.environ["TB_TOKEN"]

logging.basicConfig(format='%(asctime)s - TelegramBot - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("se conectó: " + str(update.message.from_user.id))
    if update.message.from_user.first_name:
        nombre=update.message.from_user.first_name
    else:
        nombre=""
    if update.message.from_user.last_name:
        apellido=update.message.from_user.last_name
    else:
        apellido=""
    kb = [["Destello"],["Modo"],["Relé"]]
    await context.bot.send_message(update.message.chat.id, text="Bienvenido al Bot "+ nombre + " " + apellido,reply_markup=ReplyKeyboardMarkup(kb))

async def acercade(update: Update, context):
    await context.bot.send_message(update.message.chat.id, text="Este bot fue creado para el curso de IoT FIO")


async def update_setpoint(update: Update, context):
    # Verifica si se paso el setpoint como parámetro.
    if not context.args:
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text="⚠️ Falta indicar el valor del setpoint."
        )
        return

    # Verifica si el setpoint es un número.
    try:
        setpoint = float(context.args[0])
    except ValueError:
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text="⚠️ El valor del setpoint debe ser un número válido."
        )
        return

    # Si existe y es número, continúa con el resto
    await context.bot.send_message(
        chat_id=update.message.chat.id,
        text=f"✅ Cambiando SetPoint a {setpoint} °C."
    )


async def button_handler(update: Update, context):
    mensaje = update.message.text
    logging.info(f"Mensaje recibido: {mensaje}")

    if mensaje == "Destello":
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text="⚡ Se destellaaaaaaaaa"
        )
    elif mensaje == "Relé":
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text="🔌 Activando el relé"
        )
    elif mensaje == "Modo":
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text="🔄 Cambiando de modo"
        )
    else:
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            text="❓ Comando desconocido"
        )


def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('about', acercade))

    application.add_handler(CommandHandler('setpoint', update_setpoint))
    application.add_handler(MessageHandler(filters.Regex("^(Destello|Relé|Modo)$"), button_handler))
    application.run_polling()

if __name__ == '__main__':
    main()
