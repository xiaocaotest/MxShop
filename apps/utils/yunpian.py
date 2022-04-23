import requests
import json


class YunPian:
    def __init__(self, api_key):
        self.api_key = api_key
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self, code, mobile):
        # 需要传递的参数
        params = {
            "apikey": self.api_key,
            "mobile": mobile,
            "text": f"【Hubery_Jun 生鲜超市】您的验证码是 {code}，1 分钟有效。如非本人操作，请忽略本短信"
        }
        print(params)
        response = requests.post(self.single_send_url, data=params)
        print(response.status_code, response.text)
        re_dict = json.loads(response.text)
        return re_dict


if __name__ == '__main__':
    yun_pian = YunPian("9b11127a9701975c734b8aee81ee3526")
    yun_pian.send_sms("2022", "15555151447")
