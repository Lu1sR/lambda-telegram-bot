import json, re
import boto3
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from typing import Union, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, Bot
sqs = boto3.client('sqs')
sqs_url = 'https://sqs.us-east-1.amazonaws.com/934396891861/redPython-dev-generate-qr-queue'
bot = Bot(token="")
dispatcher = Dispatcher(bot, None, use_context=True)
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# for validating an Email
def check(email):
    if(re.fullmatch(EMAIL_REGEX, email)):
        return True
    else:
        return False  
def build_menu(
    buttons: List[InlineKeyboardButton],
    n_cols: int,
    header_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]]=None,
    footer_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]]=None
) -> List[List[InlineKeyboardButton]]:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons if isinstance(header_buttons, list) else [header_buttons])
    if footer_buttons:
        menu.append(footer_buttons if isinstance(footer_buttons, list) else [footer_buttons])
    return menu

def generate_qr(update, context):
    print("hola")
    query = update.callback_query
    context.user_data["qr_number"]  = query.data.split('_')[-1]
    query.answer()
    query.edit_message_text(text="Ingrese el correo electronico")
    #context.bot.send_message(chat_id=update.message.chat_id, text= "Ingrese el correo electronico")

def start_handler(update, context):
    update.message.reply_text("Holaa")

def generate_handler(update,context):
    button_list = [
        InlineKeyboardButton("1", callback_data="generate_qr_1"),
        InlineKeyboardButton("2", callback_data="generate_qr_2"),
        InlineKeyboardButton("3", callback_data="generate_qr_3"),
        InlineKeyboardButton("4", callback_data="generate_qr_4"),
        InlineKeyboardButton("5", callback_data="generate_qr_5"),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    context.bot.send_message(update.effective_chat.id, "Numero de entradas", reply_markup=reply_markup)

def get_email_handler(update, context) -> None:
    text = update.message.text
    qrs= context.user_data["qr_number"]
    if check(text):
        print('send to SQS queue')
        sqs.send_message(
            QueueUrl= sqs_url,
            MessageBody=json.dumps({"email": text, "number": qrs})
        )
        context.bot.send_message(update.effective_chat.id, f"Se ha enviado un correo con {qrs} entradas al correo: {text}")

# def echo(update, context):

    
#     chat_id = update.message.chat_id
#     chat_user = update.message.from_user
#     chat_text = update.message.text
    
#     context.bot.send_message(chat_id=chat_id, text= "Message from " + str(chat_user.first_name) + ": \n " + chat_text)

def hello(event, context):
    
    dispatcher.add_handler(CommandHandler("start", start_handler))
    dispatcher.add_handler(CommandHandler("generate", generate_handler))
    dispatcher.add_handler(CallbackQueryHandler(generate_qr, pattern="generate_qr_"))
    dispatcher.add_handler(MessageHandler(Filters.text, get_email_handler))
   
    try:
        dispatcher.process_update(
            Update.de_json(json.loads(event["body"]), bot)
        )

    except Exception as e:
        print(e)
        return {"statusCode": 500}

    return {"statusCode": 200}
