import json

import requests
from django.conf import settings

from apps.utils.enums import SMSEnum
from apps.utils.generic import format_phone_number
from config.settings import BULK_SMS_TOKEN, BULK_SMS_URL, SMS_FROM


class SMSHandler:
    def __init__(self, sender=SMS_FROM, to=None, msg=None):
        self.sms_sender = sender
        self.sms_to = [to]
        self.sms_msg = msg
        self.base = "https://netbulksms.com/index.php"

    def send(self):
        data = {
            "api_token": BULK_SMS_TOKEN,
            "from": "AGROCONET",
            "dnd": 1,
            "to": self.sms_to,
            "body": self.sms_msg,
        }
        response = requests.post(BULK_SMS_URL, params=data)
        return response

    def send_champ(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.SEND_CHAMP_TOKEN}",
        }
        payload = {
            "message": self.sms_msg,
            "sender_name": "FarmFeat",
            "route": "dnd",
            "to": self.validate_number(),
        }
        resp = requests.post(SMSEnum.SENDCHAMP, data=json.dumps(payload), headers=headers)
        data = resp.json()
        if data.get("status") == "success":
            return True
        else:
            return False

    def validate_number(self):
        num_list = []
        for number in self.sms_to:
            rn = format_phone_number(number)
            num_list.append(rn)
        return num_list
