# -*- coding: utf-8 -*-
# @Time    : 2023/8/5 18:18
# @Author  : chenxi
# @FileName: generate_character.py
# @Software: PyCharm
# @github  ：https://github.com/LC1332/Chat-Haruhi-Suzumiya

import argparse
import configparser
import json
import random
import utils
from checkCharacter import checkCharacter
import os
import openai


# TODO

# 在这个文件中 重新实现embedding，替换 get_embedding

# 把原来的embedding函数 在这里做一个 镜像

# 这里可以有一个比如叫chinese_embedding 的函数 return get_embedding(model, text)
# 这个可以

# 你要实现一个if_chinese的函数，判断一个sentence是不是英文为主

# 建立一个combine_embedding函数， 先调用if_chinese然后再调用chinese_embedding或者english_embedding

# 一定要用 openai text-embedding-ada-002

# 写完之后，在test_kyon_generator.ipynb中跑通
# on the fly 增加 Hermione和Malfoy这两个人物

# 然后测试通他们对应的jsonl
def get_embedding_for_english(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


def get_embedding(model, texts):
    if isinstance(texts, list):
        index = random.randint(0, len(texts) - 1)
        if utils.is_chinese_or_english(texts[index]) == "chinese":
            return utils.get_embedding(model, texts), "chinese"
        else:
            return [get_embedding_for_english(text) for text in texts], "english"
    else:
        if utils.is_chinese_or_english(texts) == "chinese":
            return utils.get_embedding(model, texts), "chinese"
        else:
            return get_embedding_for_english(texts), "english"


def parse_args():
    parser = argparse.ArgumentParser(description='generate character 将台本文件保存成jsonl文件，动态创建新的角色')
    parser.add_argument('-cn_role_name', type=str, required=True, help='Chinese role name')
    parser.add_argument('-en_role_name', type=str, required=True, help='English role name')
    parser.add_argument('-prompt', default="follow me", type=str, help='prompt')
    parser.add_argument('-text_folder', required=True, type=str, help='character texts folder')
    return parser.parse_args()


class generateCharacter:
    def __init__(self, cn_role_name, en_role_name, prompt="follw me"):
        self.prompt = prompt
        self.configuration = None
        self.cn_role_name = cn_role_name
        self.en_role_name = en_role_name
        self.generate_config()
        self.image_embed_jsonl_path = self.configuration['image_embed_jsonl_path']
        self.title_text_embed_jsonl_path = self.configuration['title_text_embed_jsonl_path']
        self.images_folder = self.configuration['images_folder']
        self.texts_folder = self.configuration['texts_folder']
        self.model = utils.download_models()
        # openai.api_key = "sk-A1rbhQJimhQAt7o9h" + "CxYT3BlbkFJA4odD8x3lNkUTNIcb5U5"


    def generate_config(self):
        # 在config.ini中加添角色信息
        config = configparser.ConfigParser()
        # 读取配置文件
        config.read('config.ini', encoding='utf-8')
        configuration = {}
        if self.cn_role_name in config.sections():
            print(f"已存在{self.cn_role_name}角色的配置文件")
        else:
            # 添加新的配置项
            config.add_section(self.cn_role_name)
            config[self.cn_role_name]['character_folder'] = f"../characters/{self.en_role_name}"
            config[self.cn_role_name][
                'image_embed_jsonl_path'] = f"../characters/{self.en_role_name}/jsonl/image_embed.jsonl"
            config[self.cn_role_name][
                'title_text_embed_jsonl_path'] = f"../characters/{self.en_role_name}/jsonl/title_text_embed.jsonl"
            config[self.cn_role_name]['images_folder'] = f"../characters/{self.en_role_name}/images"
            config[self.cn_role_name]["jsonl_folder"] = f"../characters/{self.en_role_name}/jsonl"
            config[self.cn_role_name]['texts_folder'] = f"../characters/{self.en_role_name}/texts"
            config[self.cn_role_name]['system_prompt'] = f"../characters/{self.en_role_name}/system_prompt.txt"
            config[self.cn_role_name]['dialogue_path'] = f"../characters/{self.en_role_name}/dialogues/"
            config[self.cn_role_name]['max_len_story'] = "1500"
            config[self.cn_role_name]['max_len_history'] = "1200"
            config[self.cn_role_name]['gpt'] = "True"
            config[self.cn_role_name]['local_tokenizer'] = "THUDM/chatglm2-6b"
            config[self.cn_role_name]['local_model'] = "THUDM/chatglm2-6b"
            config[self.cn_role_name]['local_lora'] = "Jyshen/Chat_Suzumiya_GLM2LoRA"
            # 保存修改后的配置文件
            with open('config.ini', 'w+', encoding='utf-8') as config_file:
                config.write(config_file)
            config.read('config.ini', encoding='utf-8')
        # 检查角色文件夹
        items = config.items(self.cn_role_name)
        print(f"正在加载: {self.cn_role_name} 角色")
        for key, value in items:
            configuration[key] = value
        checkCharacter(configuration)

        # 写入prompt
        prompt = self.prompt
        with open(os.path.join(f"../characters/{self.en_role_name}", 'system_prompt.txt'), 'w+',
                  encoding='utf-8') as f:
            f.write(prompt)
            print("system_prompt.txt已创建")
        self.configuration = configuration

    def generate_jsonl(self):
        title_text_embed = []
        title_text = []
        for file in os.listdir(self.texts_folder):
            if file.endswith('.txt'):
                title_name = file[:-4]
                with open(os.path.join(self.texts_folder, file), 'r', encoding='utf-8') as fr:
                    title_text.append(f"{title_name}link{fr.read()}")
        # texts_embeddings, res = get_embedding(self.model, title_text)
        # embeddings = texts_embeddings if res == "english" else [embed.cpu().tolist() for embed in texts_embeddings]
        for title_text, embed in zip(title_text, utils.get_embedding(self.model, title_text)):
            title_text_embed.append({title_text: embed.cpu().tolist()})
        self.store(self.title_text_embed_jsonl_path, title_text_embed)

        if len(os.listdir(self.images_folder)) != 0:
            image_embed = []
            images = []
            for file in os.listdir(self.images_folder):
                images.append(file[:-4])
            # images_embeddings, res = get_embedding(self.model, images)
            # embeddings = images_embeddings if res == "english" else [embed.cpu().tolist() for embed in images_embeddings]
            for image, embed in zip(images, utils.get_embedding(self.model, images)):
                image_embed.append({image: embed.cpu().tolist()})
            self.store(self.image_embed_jsonl_path, image_embed)

    def store(self, path, data):
        with open(path, 'w+', encoding='utf-8') as f:
            for item in data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')


if __name__ == '__main__':
    # res = get_embedding_for_english("hello")
    # print(type(res), res)
    args = parse_args()
    cn_role_name = args.cn_role_name
    en_role_name = args.en_role_name
    prompt = args.prompt
    text_folder = args.text_folder
    # ini 生成角色配置文件
    run = generateCharacter(cn_role_name, en_role_name, prompt)
    run.generate_config()
    run.generate_jsonl()

