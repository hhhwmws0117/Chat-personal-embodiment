# -*- coding: utf-8 -*-
# @Time    : 2023/9/20 19:24
# @Author  : chenxi
# @FileName: download_data.py
# @Software: PyCharm
from chatharuhi import ChatHaruhi
import zipfile
import os
import requests

NAME_DICT = {'汤师爷': 'tangshiye', '慕容复': 'murongfu', '李云龙': 'liyunlong', 'Luna': 'Luna', '王多鱼': 'wangduoyu',
             'Ron': 'Ron', '鸠摩智': 'jiumozhi', 'Snape': 'Snape',
             '凉宫春日': 'haruhi', 'Malfoy': 'Malfoy', '虚竹': 'xuzhu', '萧峰': 'xiaofeng', '段誉': 'duanyu',
             'Hermione': 'Hermione', 'Dumbledore': 'Dumbledore', '王语嫣': 'wangyuyan',
             'Harry': 'Harry', 'McGonagall': 'McGonagall', '白展堂': 'baizhantang', '佟湘玉': 'tongxiangyu',
             '郭芙蓉': 'guofurong', '旅行者': 'wanderer', '钟离': 'zhongli',
             '胡桃': 'hutao', 'Sheldon': 'Sheldon', 'Raj': 'Raj', 'Penny': 'Penny', '韦小宝': 'weixiaobao',
             '乔峰': 'qiaofeng', '神里绫华': 'ayaka', '雷电将军': 'raidenShogun', '于谦': 'yuqian'}



try:
  os.makedirs("characters_zip")
except:
  pass
try:
  os.makedirs("characters")
except:
  pass
ai_roles_obj = {}
for ai_role_en in NAME_DICT.values():
  file_url = f"https://github.com/LC1332/Haruhi-2-Dev/raw/main/data/character_in_zip/{ai_role_en}.zip"
  try:
    os.makedirs(f"characters/{ai_role_en}")
  except:
    pass
  if f"{ai_role_en}.zip" not in os.listdir(f"characters_zip"):
    destination_file = f"characters_zip/{ai_role_en}.zip"
    max_retries = 3  # 最大重试次数
    for attempt in range(1, max_retries+1):
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(destination_file, "wb") as file:
                file.write(response.content)
            print(ai_role_en)
            break
        else:
            print(f"{ai_role_en}第{attempt}次下载失败")
    # wget.download(file_url, destination_file)  # 503
    destination_folder = f"characters/{ai_role_en}"
    with zipfile.ZipFile(destination_file, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)
  db_folder = f"./characters/{ai_role_en}/content/{ai_role_en}"
  system_prompt = f"./characters/{ai_role_en}/content/system_prompt.txt"
  ai_roles_obj[ai_role_en] = ChatHaruhi(system_prompt=system_prompt,
                        llm="openai",
                        story_db=db_folder,
                        verbose=True)