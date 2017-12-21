import os
import sys
import json
import requests

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])


@app.route('/', methods=['GET'])
def verify():
    return "Hello Folks! My name is Echo Bot", 200


# Webhook POST
@app.route('/facebook', methods=['GET', 'POST'])
def facebook():
    if request.method == 'POST':
        # endpoint for processing incoming messaging events
        data = request.get_json()
        log(data)  # you may not want to log every incoming message in production, but it's good for testing

        if data["object"] == "page":

            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:

                    if messaging_event.get("message"):  # someone sent us a message

                        # sender_id = messaging_event["sender"]["id"]
                        recipient_id = messaging_event["recipient"]["id"]
                        message_text = messaging_event["message"]["text"]

                        # send_message(sender_id, message_text)
                        payload = json.dumps({
                            "recipient": {
                                "id": recipient_id
                            },
                            "message": {
                                "text": message_text
                            }
                        })

                        # send to qismo and let it handle the delivery
                        send_to_qismo(payload, channel="fb", qiscus_app_id=data.get("qiscus_app_id"))

                    if messaging_event.get("delivery"):  # delivery confirmation
                        pass

                    if messaging_event.get("optin"):  # optin confirmation
                        pass

                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                        pass

        return "ok", 200
    else:
        # when the endpoint is registered as a webhook, it must echo back
        # the 'hub.challenge' value it receives in the query arguments
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200
        else:
            return "Not Found", 404


@app.route('/line', methods=['POST'])
def line():
    # get X-Line-Signature header value
    # signature = request.headers['X-Line-Signature']
    payload = request.get_json()
    log(payload)

    # get request body as text
    # body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        # handler.handle(body, signature)
        events = payload.get("events")[0]
        data = json.dumps({
            "replyToken": events.get("replyToken"),
            "messages": [
                {
                    "type": events.get("message").get("type"),
                    "text": events.get("message").get("text")
                }
            ]
        })
        send_to_qismo(data, channel="line", qiscus_app_id=payload.get("qiscus_app_id"))
    except InvalidSignatureError:
        abort(400)

    return 'OK'


APP_ID = os.environ.get("APP_ID")
SECRET_KEY = os.environ.get("SECRET_KEY")
BOT_EMAIL = os.environ.get("BOT_EMAIL")
QISCUS_SDK_URL = os.environ.get("QISCUS_SDK_URL")
POST_URL = "{}/api/v2/rest/post_comment".format(QISCUS_SDK_URL)
HEADERS = {"QISCUS_SDK_SECRET": SECRET_KEY}


@app.route('/qiscus', methods=['POST'])
def qiscus():
    payload = request.get_json().get('payload')
    qiscus_app_id = request.get_json().get('qiscus_app_id')

    room_id = payload.get("room").get("id")
    message = payload.get("message").get("text")

    data = {
        "sender_email": BOT_EMAIL,
        "room_id": room_id,
        "message": message,
        "type": "text",
        "payload": json.dumps(payload) or {}
    }

    # send to qismo
    req = send_to_qismo(data, channel="qiscus", qiscus_app_id=qiscus_app_id)
    # req = requests.post(POST_URL, headers=HEADERS, params=data)

    return "OK", 200 if req.status_code == 200 else "Failed", req.status_code


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


def send_to_qismo(payload, channel=None, qiscus_app_id=APP_ID):
    base_url = "http://qismo-stag.herokuapp.com"

    headers = {
        "Content-Type": "application/json"
    }

    if channel == "fb":
        url = "{}/{}/fb/bot".format(base_url, qiscus_app_id)

    elif channel == "line":
        url = "{}/{}/line/bot".format(base_url, qiscus_app_id)

    else:
        url = "{}/{}/qiscus/bot".format(base_url, qiscus_app_id)

    log(url)
    log(payload)

    # TODO: add params and headers
    r = requests.post(url, headers=headers, data=payload)
    rb = requests.post('https://requestb.in/1e63rom1', headers=headers, data=payload)

    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    return r


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    rb = requests.post('https://requestb.in/1e63rom1', data=data)

    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    if rb.status_code != 200:
        log(rb.status_code)
        log(rb.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
