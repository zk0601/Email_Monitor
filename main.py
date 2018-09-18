import requests
import yaml
import datetime
import os
import json
from EMAIL import Post_email

Yaml_File = os.path.join(os.path.dirname(__file__), "options.yaml")
log_file = os.path.join(os.path.dirname(__file__), "log")


def eth_balance_monitor():
    email_text = ''
    url = 'http://127.0.0.1:8000/eth/get_hourbalance'
    date_format = "%Y%m%d %H"
    now_hour = datetime.datetime.now()
    last_hour = now_hour + datetime.timedelta(hours=-1)
    now_hour, last_hour = now_hour.strftime(date_format), last_hour.strftime(date_format)
    now_hour_res = requests.post(url, data={'date': now_hour})
    last_hour_res = requests.post(url, data={'date': last_hour})
    now_data_dict, last_data_dict = json.loads(now_hour_res.content)['data'], json.loads(last_hour_res.content)['data']
    body_text_list = []
    with open(Yaml_File, 'rb') as f:
        monitor_level = yaml.load(f)['monitor_setting']['ETH']['Balance_level'][0]
    for plat in now_data_dict.keys():
        if abs(float(last_data_dict[plat]) - float(now_data_dict[plat])) >= monitor_level:
            now_time_str = "%s，%s" % tuple(now_hour.split())
            last_time_str = "%s，%s" % tuple(last_hour.split())
            body_text = "<p>根据《曲速小程序》监测，%s平台于%s点到%s点，ETH余额从%s变化到%s，%s个ETH进行了交易</p>" % \
                        (plat,  last_time_str, now_time_str, str(last_data_dict[plat]), str(now_data_dict[plat]), str(round(abs(float(last_data_dict[plat]) - float(now_data_dict[plat])), 4)))
            body_text_list.append(body_text)
    if not len(body_text_list) == 0:
        email_text = ''.join(body_text_list)
    return email_text


def eth_trade_monitor():
    email_text = ''
    url = 'http://127.0.0.1:8000/eth/get_trade'
    body_text_list = []
    date_format = "%Y%m%d %H"
    last_hour = datetime.datetime.now() + datetime.timedelta(hours=-1)
    last_hour = last_hour.strftime(date_format)
    plat_list = ['Okex', 'huobi', '币安', 'Bitfinex', 'UpBit', 'P网', 'GATE']
    with open(Yaml_File, 'rb') as f:
        monitor_level = yaml.load(f)['monitor_setting']['ETH']['Trade_value_level'][0]
    for plat in plat_list:
        sub_body_text_list = []
        post_data = {'time': last_hour, 'platform': plat, 'value_level': monitor_level}
        res = requests.post(url, post_data)
        data = json.loads(res.content)['data']
        for item in data:
            if float(item["value"]) >= monitor_level:
                trade_url = "https://etherscan.io/tx/" + item["trade_hash"]
                body_text = "<p>根据《曲速小程序》监测, %s平台的%s地址，在%s时间，发生了如下交易：FROM_ADDRESS:%s, TO_ADDRESS:%s, VALUE:%sETH</p>" \
                            "</p>交易详情地址：<a href=%s>%s</a></p>" % \
                            (plat, item["from_address"], item["trade_time"], item["from_address"], item["to_address"], item["value"], trade_url, trade_url)
                sub_body_text_list.append(body_text)
        if not len(sub_body_text_list) == 0:
            sub_body_text_list.append('##########################################################')
            body_text_list.append('\n'.join(sub_body_text_list))
    if not len(body_text_list) == 0:
        email_text = ''.join(body_text_list)
    return email_text


def eth_monitor(balance_text, trade_text):
    if not balance_text and not trade_text:
        return
    email_text = "<html><body><h1>余额监控：</h1>" + balance_text + "<h1>交易监控：</h1>" + trade_text + "</body></html>"
    header = "ETH监控邮件"
    email = Post_email()
    email.send_email(email_text, header)


if __name__ == '__main__':
    while True:
        try:
            balance_text = eth_balance_monitor()
            trade_text = eth_trade_monitor()
            eth_monitor(balance_text, trade_text)
            break
        except Exception as e:
            with open(log_file, 'a') as f:
                f.write(str(e))
            continue

