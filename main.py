import configparser
from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random


class Config:
  def __init__(self, config_file):
    self.cf = configparser.ConfigParser()
    self.cf_file = config_file

    if not config_file or not os.path.isfile(self.cf_file):
      raise "no config file"

    self.cf.read(self.cf_file, encoding="utf-8")

  def write(self):
    with open(self.cf_file, "w", encoding="utf-8") as f:
      self.cf.write(f)
      f.flush()
today = datetime.now()

config = Config("setting.ini")
app_id = config.cf.get("DATA", "app_id")
app_secret = config.cf.get("DATA", "app_secret")
user_id = config.cf.get("DATA", "user_id")
template_id = config.cf.get("DATA", "template_id")
birthday = config.cf.get("DATA", "birthday")
city = config.cf.get("DATA", "city")
start_date = config.cf.get("DATA", "start_date")

data_dict = {}


def get_weather():
    global data_dict
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city

    res = requests.get(url).json()
    weather = res['data']['list'][0]
    data_dict['date'] = weather['date']
    data_dict['weather'] = weather['weather']
    data_dict['low'] = weather['low']
    data_dict['high'] = weather['high']


def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days+1

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
get_weather()
works = get_words()
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
data = {
        "date": {"value": data_dict['date'], "color": get_random_color()},
        "city": {"value": city, "color": get_random_color()},
        "weather": {"value": data_dict['weather'], "color": get_random_color()},
        "low": {"value": int(data_dict['low']), "color": get_random_color()},
        "high": {"value": int(data_dict['high']), "color": get_random_color()},
        "days": {"value": get_count(), "color": get_random_color()},
        "birthday_left": {"value": get_birthday(), "color": get_random_color()},
        "words": {"value": works, "color": get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
print(data)
