from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import paho.mqtt.client as mqtt

app = Flask(__name__)

# 設定你的 LINE BOT channel secret 和 access token
LINE_CHANNEL_SECRET = '5b007d02a19620b6255a7584f218e0a8'
LINE_CHANNEL_ACCESS_TOKEN = 'pq/YwFAeESX3QPdC83jlb53I8uwshjM6o6Gw6yrYm22rr6Lck9BWoCDXX9LFBo4lzSnUywc28SK/ltkhab/9Ue6rI1NuKTc/jnbRd5xMpOo6vulS74RVVmT7wEXIaINIPPvO3khIyND6srkkst+zigdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# MQTT Broker 的設定
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "school/relay"

# 建立 MQTT 客戶端
mqtt_client = mqtt.Client()

# 連接到 MQTT Broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 Line 的簽名
    signature = request.headers['X-Line-Signature']

    # 獲取請求的 body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證簽名並處理訊息
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    # 這裡將接收到的文字訊息發佈到 MQTT
    mqtt_client.publish(MQTT_TOPIC, user_message)
    
    # 回覆使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f'MQTT message "{user_message}" sent!')
    )

if __name__ == "__main__":
    app.run
