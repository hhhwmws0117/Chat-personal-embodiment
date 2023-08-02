'''
Affiliated to the project 'Chat-Haruhi'
Edited by 睡觉鱼 on 2 Aug
'''
import configparser
from ChatGPT import ChatGPT
import json

# Open a configuration file
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
print(config['凉宫春日']['image_embed_jsonl_path'])
characters = ['凉宫春日','李云龙','神里绫华']
#characters = ['凉宫春日','李云龙','于谦','李鲁鲁','王多鱼','汤师爷','韦小宝']

questions = []
with open('16.txt','r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        if line != '\n':
            questions.append(line.strip())

data = []
for character in characters:
    print(f'正在加载{character}的数据')
    conf = config[character]
    llm = ChatGPT(conf)
    llm.preload()
    #print(llm.get_response('你是谁', chat_history_tuple=()))
    responses = []
    for question in questions:
        query = '请假设你是该角色，并以该角色的心理特点回答以下问题：'+question+'如果从完全不符合到完全符合的程度分别为1-7分，你认为你是几分？'
        answer = llm.get_response(query, chat_history_tuple=())
        qa = {'question':question,'answer':answer}
        responses.append(qa)

    dict = {'character':character,'responses':responses}
    data.append(dict)

with open('data.json','w') as f:
    json.dump(data,f,ensure_ascii=False)
    print('完成生成！')