import hashlib
import json
import os
import random
from datetime import datetime
from zipfile import ZipFile
from queue import Queue
import time
import gradio as gr
from app import ChatPerson, ChatSystem
from text import Text
import threading
from baichuanAgent import chatAgent
from generate_character import generateCharacter

left_eval = ""
right_eval = ""
stopping = False
with open('./fist_questions.txt', 'r', encoding='utf-8') as f:
    first_questions = f.read().strip().split("\n")


def create_gradio(chat_system, chat_system2, chat_system3):
    character_list = chat_system.getAllCharacters()
    left_character_list = random.sample(character_list, int(len(character_list) / 2))
    right_character_list = [item for item in character_list if item not in left_character_list]

    # from google.colab import drive
    # drive.mount(drive_path)
    def generate_user_id(ip_address):
        hash_object = hashlib.sha256(ip_address.encode())
        return hash_object.hexdigest()

    # def save_response(chat_history_tuple):
    #     with open(f"{chat_person.ChatGPT.dialogue_path}/conversation_{time.time()}.txt", "w", encoding='utf-8') as file:
    #         for cha, res in chat_history_tuple:
    #             file.write(cha)
    #             file.write("\n---\n")
    #             file.write(res)
    #             file.write("\n---\n")

    def respond(role_name, user_message, chat_history, character, request: gr.Request):
        # print("history is here : ", chat_history)
        # character = character.value
        print("the character is : ", character)
        input_message = role_name + ':「' + user_message + '」'
        bot_message = chat_system.getResponse(input_message, chat_history, character)
        chat_history.append((input_message, bot_message))
        # chat_system.addChatHistory(character, chat_history)
        return "", chat_history, bot_message

    def checkMessage(role1, role2, chat_history):
        print("chat_history", chat_history)
        if len(chat_history) != 0:
            global stopping
            messages = ""
            for lis in chat_history:
                print("lis", lis)
                messages += lis[0] + "\n" + lis[1] + "\n"
            res = checkMessage(character1, character2, chat_history)
            response = ""
            if res.empty() is not None:
                response += res.get()
            stopping = True if "True" in response else False
            print("stopping", stopping)
        from baichuanAgent import chatAgent
        prompt = f"""你是一名高校的心理学教授叫做{role1}，正在邀请学生{role2}回答问题做心理测试
请参考你们的聊天记录：
{chat_history}
你需要根据春日的回答探究是否你们的聊天是否对某一事件达成一致
如果达成一致
请返回`True`
否则返回`False`

example input：
{role1}： 我们去吃饭把
{role2}：好的呀
example output：
True

example input:
{role1}： 我们去吃饭把
{role2}：吃什么
example output:
False"""
        print(prompt)
        messages = [{"role": "user", "content": prompt}]
        responses = chatAgent(messages)
        return_msg = ""
        while not responses.empty():
            return_msg += responses.get()  # TODO 做成流式输出
        print("stopping:\n", return_msg)
        return return_msg

    def dialogueA(left_character, right_character, chat_history):
        print(left_character)
        global stopping

        stopping = False
        chat_history = []  # 这里先清空历史记录。目前没有实现双方对话几轮之后被停止，然后又开始对话的功能。如果要实现，要考虑用户两次点击的先说的人不一样，这点处理历史记录很麻烦。所以这里先直接清空
        # input_message = left_character + ':「' + right_character + '你有什么兴趣爱好吗？' + '」'
        question = random.sample(first_questions, 1)[0]
        input_message = left_character + ':「' + question + '」'
        for i in range(20):
            if i == 0 and chat_history == []:  # 第一轮
                right_message = chat_system3.getResponse(input_message, chat_history, right_character)
                chat_history.append((input_message, right_message))
            else:
                left_message = chat_system2.getResponse(right_message, chat_history, left_character, first_person=True)
                right_message = chat_system3.getResponse(left_message, chat_history, right_character)
                chat_history.append((left_message, right_message))

            if stopping:
                global left_eval, right_eval
                left_eval = chatAgent([{'role': 'user',
                                        'content': "假设你是一个人类情感与性格分析师，请尝试从以下对话中分别阐述对话中出现的" + left_character + f"{right_character}和情感、性格特点、mbti人格。并判断两个人是否有可能成为恋人。对话：" + '\n'.join(
                                            [' - '.join(msg) for msg in chat_history])}])
                right_eval = chatAgent([{'role': 'user',
                                         'content': f"假设你是一个人类情感与性格分析师，请尝试从以下对话中分别阐述对话中出现的{left_character} 和" + right_character + "的情感与性格特点。mbti人格。并判断两个人是否有可能成为恋人。对话：" + '\n'.join(
                                             [' - '.join(msg) for msg in chat_history])}])

                stopping = False
                yield chat_history
                return
            yield chat_history

    def dialogueB(left_character, right_character, chat_history):
        print(right_character)
        global stopping
        stopping = False
        chat_history = []  # 这里先清空历史记录。目前没有实现双方对话几轮之后被停止，然后又开始对话的功能。如果要实现，要考虑用户两次点击的先说的人不一样，这点处理历史记录很麻烦。所以这里先直接清空
        # input_message = right_character + ':「' + "你好呀," + left_character + '你有什么兴趣爱好吗？' + '」'
        input_message = right_character + ':「' + random.sample(first_questions, 1)[0] + '」'
        left_message = right_message = ""
        for i in range(20):
            if i == 0 and chat_history == []:  # 第一轮
                left_message = chat_system2.getResponse(input_message, chat_history, left_character)
                chat_history.append((input_message, left_message))
            else:
                right_message = chat_system3.getResponse(left_message, chat_history, right_character, first_person=True)
                left_message = chat_system2.getResponse(right_message, chat_history, left_character)
                chat_history.append((right_message, left_message))
            if stopping:
                global right_eval, left_eval
                left_eval = chatAgent([{'role': 'user',
                                        'content': "假设你是一个人类情感与性格分析师，请尝试从以下对话中分别阐述对话中出现的" + left_character + "的情感与性格特点。对话：" + '\n'.join(
                                            [' - '.join(msg) for msg in chat_history])}])
                # right_eval = chatAgent([{'role': 'user',
                #                          'content': "假设你是一个人类情感与性格分析师，请尝试从以下对话中分别阐述对话中出现的" + right_character + "的情感与性格特点。对话：" + '\n'.join(
                #                              [' - '.join(msg) for msg in chat_history])}])

                stopping = False
                yield chat_history
                return
            yield chat_history

    def getImage(query, character):
        pass
        return chat_system.getImage(query, character)
        # return chat_person.ChatGPT.text_to_image(query)

    def switchCharacter(characterName, chat_history):
        pass
        chat_history = []
        chat_system.addCharacter(character=characterName)
        # chat_history = chat_system.getChatHistory(characterName)
        return chat_history, None
        # chat_history = []
        # chat_person.switchCharacter(characterName)
        # # print(chat_person.ChatGPT.image_path)
        # return chat_history, None

    def switchOneCharacterA(characterName, chat_history):  # TODO 双人对话中切换一个角色。或许和SwitchCharacter()非常类似。
        chat_history = [];
        chat_system2.addCharacter(character=characterName);
        return chat_history

    def switchOneCharacterB(characterName, chat_history):  # TODO 双人对话中切换一个角色。或许和SwitchCharacter()非常类似。
        chat_history = [];
        chat_system3.addCharacter(character=characterName);
        return chat_history

    def generateCustomCharacter(cn_role_name, en_role_name, prompt, file_obj):
        run = generateCharacter(cn_role_name, en_role_name, prompt)
        run.generate_config()
        with ZipFile(file_obj.name) as zfile:
            zfile.extractall(run.texts_folder)
        run.generate_jsonl()
        return {res: gr.update(visible=True)}

    with gr.Blocks() as demo:
        gr.Markdown(
            """
            ## Chat-personal-embodiment 个人化身
            - 项目地址 [https://github.com/hhhwmws0117/Chat-personal-embodiment](https://github.com/hhhwmws0117/Chat-personal-embodiment)
            """
        )
        with gr.Tab("Chat-Embodiment") as chat:
            character = gr.Radio(character_list, label="Character", value='凉宫春日')
            image_input = gr.Textbox(visible=False)
            japanese_input = gr.Textbox(visible=False)
            with gr.Row():
                chatbot = gr.Chatbot()
                image_output = gr.Image()
            audio = gr.Audio(visible=False)
            role_name = gr.Textbox(label="角色名")
            msg = gr.Textbox(label="输入")
            with gr.Row():
                clear = gr.Button("Clear")
                image_button = gr.Button("给我一个图")
                # audio_btn = gr.Button("春日和我说")
            # japanese_output = gr.Textbox(interactive=False, visible=False)
            sub = gr.Button("Submit")
            # audio_store = gr.Textbox(interactive=False)

            # def update_audio(audio, japanese_output):
            #     japanese_output = japanese_output.split("春日:")[1.txt]
            #     jp_audio_store = vits_haruhi.vits_haruhi(japanese_output, 4)
            #     return gr.update(value=jp_audio_store, visible=True)

            character.change(fn=switchCharacter, inputs=[character, chatbot], outputs=[chatbot, image_output])

            clear.click(lambda: None, None, chatbot, queue=False)
            # msg.submit(respond, [role_name, msg, chatbot], [msg, chatbot, image_input, japanese_output])
            msg.submit(respond, [role_name, msg, chatbot, character], [msg, chatbot, image_input])
            # sub.click(fn=respond, inputs=[role_name, msg, chatbot], outputs=[msg, chatbot, image_input, japanese_output])
            sub.click(fn=respond, inputs=[role_name, msg, chatbot, character], outputs=[msg, chatbot, image_input])
            # audio_btn.click(fn=update_audio, inputs=[audio, japanese_output], outputs=audio)

            image_button.click(getImage, inputs=[image_input, character], outputs=image_output)
        with gr.Tab("Custom Character"):
            format_rule = """
    台本格式：台本文件夹打包成zip
        文件名为剧情内容.txt
        示例：
            fileName: SOS团起名由来.txt
            fileContent:
                春日:「社团名字我刚刚已经想到了!」
                阿虚:「……那你说来听听啊!」
                春日:「SOS团!让世界变得更热闹的凉宫春日团，简称SOS团。」"""
    # 图片格式：图片文件夹打包成zip
    #     图片名即为与该图片相似的文本  如 SOS团.jpg"""
            with gr.Column() as gen:
                with gr.Row():
                    with gr.Column():
                        # role_name
                        with gr.Row():
                            cn_role_name = gr.Textbox(label="cn_role_name")
                            en_role_name = gr.Textbox(label="en_role_name")
                        texts = gr.File(label="Upload Texts")
                        prompt = gr.Textbox(label="Edit Prompt")
                        # images = gr.File(label="Upload Images")
                    rule = gr.Textbox(label="文件格式", lines=10)
                    rule.value = format_rule
                res = gr.Textbox(label="res_msg", placeholder=f"已生成个人数字化身{cn_role_name.value}", visible=False)
                generate_btn = gr.Button("生成")
                generate_btn.click(fn=generateCustomCharacter, inputs=[cn_role_name, en_role_name, prompt, texts], outputs=res)



        def stopChat():
            global stopping
            stopping = True
            return

        def feval_A(chat_history):
            global left_eval, right_eval
            print(left_eval)
            chat_history = []
            chat_history.append(("", "[" + "".join(str(item) for item in left_eval.queue) + "]"))

            yield chat_history

        def feval_B(chat_history):
            global left_eval, right_eval
            print(right_eval)
            chat_history = []
            chat_history.append(("", "[" + "".join(str(item) for item in right_eval.queue) + "]"))
            yield chat_history

        with gr.Tab("Dialogue of Two Embodiments"):
            with gr.Row():
                character1 = gr.Radio(character_list, label="CharacterA", value='凉宫春日')
                character2 = gr.Radio(character_list, label="CharacterB", value='凉宫春日')
            with gr.Row():
                chatbot2 = gr.Chatbot()
            with gr.Row():
                begin1 = gr.Button("角色A先说")
                begin2 = gr.Button("角色B先说")
            stop = gr.Button("Stop")
            eval_1 = gr.Button("Evaluate")
            # eval_2 = gr.Button("Evaluate B")
            with gr.Row():
                sumbot1 = gr.Chatbot()
                # sumbot2 = gr.Chatbot()

            character1.change(fn=switchOneCharacterA, inputs=[character1, chatbot2], outputs=[chatbot2])  # TODO
            character2.change(fn=switchOneCharacterB, inputs=[character2, chatbot2], outputs=[chatbot2])  # TODO
            begin1.click(fn=dialogueA, inputs=[character1, character2, chatbot2], outputs=chatbot2)  # TODO
            begin2.click(fn=dialogueB, inputs=[character1, character2, chatbot2], outputs=chatbot2)  # TODO
            # chatbot.change
            eval_1.click(fn=feval_A, inputs=[sumbot1], outputs=sumbot1, queue=False)
            # eval_2.click(fn=feval_B, inputs=[sumbot2], outputs=sumbot2, queue=False)
            stop.click(fn=stopChat, queue=False)
    demo.queue().launch(debug=True, share=True)


# chat_person = ChatPerson()
# create_gradio(chat_person)

chat_system = ChatSystem()
chat_system2 = ChatSystem()
chat_system3 = ChatSystem()
create_gradio(chat_system, chat_system2, chat_system3)
