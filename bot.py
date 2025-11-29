import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from flask import Flask, request, render_template_string
import threading

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Автоматически правильный HTTPS-адрес от Render
WEBAPP_URL = f"https://{request.host}"

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>bulUP – Пополнение Steam</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {font-family: Arial; margin:0; padding:20px; background:#1a1a1a; color:white;}
        h1 {text-align:center; color:#ff6600;}
        .grid {display:grid; grid-template-columns:repeat(2,1fr); gap:15px;}
        .item {background:#2d2d2d; padding:20px; border-radius:12px; text-align:center;}
        .item button {background:#ff6600; color:white; border:none; padding:14px; width:100%; border-radius:10px; font-size:16px;}
        #cart {background:#2d2d2d; padding:15px; border-radius:10px; margin:20px 0; font-size:18px;}
        #pay, #success {display:none; background:#2d2d2d; padding:25px; border-radius:12px; margin-top:20px;}
        input {width:100%; padding:14px; margin:10px 0; background:#333; border:none; border-radius:8px; color:white; font-size:16px;}
        button#mainpay {background:#00d26a; padding:16px; font-size:18px; border:none; border-radius:10px;}
        #success {text-align:center; font-size:20px; color:#00d26a;}
    </style>
</head>
<body>
    <h1>bulUP</h1>
    <p style="text-align:center;">Пополнение Steam кошелька</p>
    <div class="grid" id="catalog">
        <div class="item"><div>100 ₽</div><button onclick="add(100,'₽')">Купить</button></div>
        <div class="item"><div>250 ₽</div><button onclick="add(250,'₽')">Купить</button></div>
        <div class="item"><div>500 ₽</div><button onclick="add(500,'₽')">Купить</button></div>
        <div class="item"><div>1000 ₽</div><button onclick="add(1000,'₽')">Купить</button></div>
        <div class="item"><div>2000 ₽</div><button onclick="add(2000,'₽')">Купить</button></div>
        <div class="item"><div>5000 ₽</div><button onclick="add(5000,'₽')">Купить</button></div>
    </div>
    <div id="cart">Корзина пуста</div>
    <button onclick="checkout()" id="btn" style="display:none; width:100%; padding:16px; background:#ff6600; border:none; border-radius:10px; color:white; font-size:18px;">Перейти к оплате</button>
    <div id="pay">
        <h2>Оплата картой</h2>
        <input type="text" id="num" placeholder="Номер карты" maxlength="19">
        <input type="text" id="date" placeholder="MM/YY">
        <input type="text" id="cvv" placeholder="CVV" maxlength="4">
        <input type="text" id="name" placeholder="Имя держателя">
        <button id="mainpay" onclick="pay()">Оплатить</button>
    </div>
    <div id="success">
        Спасибо за покупку!<br><br>Возвращаю в меню...
    </div>
<script>
    let cart = [];
    const tg = window.Telegram.WebApp;
    tg.ready(); tg.expand();
    function add(a,c){cart=[{amount:a,cur:c}];document.getElementById('cart').innerHTML=`Выбрано: ${a} ${c}`;document.getElementById('btn').style.display='block';}
    function checkout(){document.getElementById('catalog').style.display='none';document.getElementById('cart').style.display='none';document.getElementById('btn').style.display='none';document.getElementById('pay').style.display='block';}
    function pay(){
        setTimeout(()=>{document.getElementById('pay').style.display='none';document.getElementById('success').style.display='block';
        tg.sendData(JSON.stringify({action:"success",cart:cart}));setTimeout(()=>tg.close(),3000);},1200);
    }
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Открыть bulUP", web_app=WebAppInfo(url=WEBAPP_URL)))
    bot.send_message(message.chat.id, "Привет! Это bulUP – быстрое пополнение Steam", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def webapp_data(message):
    data = json.loads(message.web_app_data.data)
    if data.get("action") == "success":
        bot.send_message(message.chat.id, "Спасибо за покупку в bulUP!\nКод будет отправлен в течение минуты")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Вернуться в bulUP", web_app=WebAppInfo(url=WEBAPP_URL)))
        bot.send_message(message.chat.id, "Хочешь купить ещё?", reply_markup=markup)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))).start()
    bot.infinity_polling()
