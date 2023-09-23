from chatharuhi import ChatHaruhi
from datetime import datetime
import zipfile
import os
import re
import requests
import gradio as gr
import openai

openai.api_key = "sk-mmJ"
os.environ["OPENAI_API_KEY"] = openai.api_key
NAME_DICT = {'汤师爷': 'tangshiye', '慕容复': 'murongfu', '李云龙': 'liyunlong', 'Luna': 'Luna',
             '王多鱼': 'wangduoyu',
             'Ron': 'Ron', '鸠摩智': 'jiumozhi', 'Snape': 'Snape',
             '凉宫春日': 'haruhi', 'Malfoy': 'Malfoy', '虚竹': 'xuzhu', '萧峰': 'xiaofeng', '段誉': 'duanyu',
             'Hermione': 'Hermione', 'Dumbledore': 'Dumbledore', '王语嫣': 'wangyuyan',
             'Harry': 'Harry', 'McGonagall': 'McGonagall', '白展堂': 'baizhantang', '佟湘玉': 'tongxiangyu',
             '郭芙蓉': 'guofurong', '旅行者': 'wanderer', '钟离': 'zhongli',
             '胡桃': 'hutao', 'Sheldon': 'Sheldon', 'Raj': 'Raj', 'Penny': 'Penny', '韦小宝': 'weixiaobao',
             '乔峰': 'qiaofeng', '神里绫华': 'ayaka', '雷电将军': 'raidenShogun', '于谦': 'yuqian'}


# download all character zip file
def download_character():
    default_path = "characters/default"
    try:
        os.makedirs(f"{default_path}/characters_zip")
    except:
        pass
    for ai_role_en in NAME_DICT.values():
        file_url = f"https://github.com/LC1332/Haruhi-2-Dev/raw/main/data/character_in_zip/{ai_role_en}.zip"
        try:
            os.makedirs(f"{default_path}/{ai_role_en}")
        except:
            pass
        if f"{ai_role_en}.zip" not in os.listdir(f"{default_path}/characters_zip"):
            destination_file = f"{default_path}/characters_zip/{ai_role_en}.zip"
            max_retries = 3  # 最大重试次数
            for attempt in range(1, max_retries + 1):
                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(destination_file, "wb") as file:
                        file.write(response.content)
                    print(ai_role_en)
                    break
                else:
                    print(f"{ai_role_en}第{attempt}次下载失败")
            # wget.download(file_url, destination_file)  # 503
            destination_folder = f"{default_path}/{ai_role_en}"
            with zipfile.ZipFile(destination_file, 'r') as zip_ref:
                zip_ref.extractall(destination_folder)


def chat_psychologist(nickname, year, month, day, sex, occupation, school, label, q1, q2, q3, q4, model="gpt-3.5-turbo",
                      dialogue_example=""):
    custom_path = "characters/custom"
    if not os.path.exists(custom_path):
        os.makedirs(custom_path)
    basic_question_list = ["昵称", "生日", "性别", "职业", "学校", "标签"]
    basic_choice_list = [nickname, f"{year}年{month}月{day}", sex, occupation, school, label]
    psych_question_list = ["你平时的周末是怎么度过的？", "你对音乐的偏好是什么？", "你最喜欢的电影类型是什么？"]
    psych_choice_list = [q1, q2, q3]
    path = f"{custom_path}/{nickname}"
    txts_path = f"{path}/story_txts"
    if not os.path.exists(path):
        os.makedirs(path)  # 创建个人角色目录
        os.makedirs(txts_path)  # 创建个人角色对话目录
        for i in range(len(psych_question_list)):
            question_string = f"{psych_question_list[i]}\n{psych_choice_list[i]}"
            # Save the string to a file with index as the name
            filename = f"{txts_path}/q{i + 1}.txt"
            with open(filename, 'w+', encoding="utf-8") as file:
                file.write(question_string)
        INDEX = 4
    else:
        list_of_dirs = os.listdir(txts_path)
        pattern = r"^q\d+\.txt$"
        matched_dirs = [s for s in list_of_dirs if re.match(pattern, s)]
        INDEX = len(matched_dirs) + 1  # 新的问题的 index
        if len(matched_dirs) > 3:
            for i, dir in enumerate(matched_dirs[3:]):
                with open(f"{txts_path}/{dir}", 'r', encoding='utf-8') as f:
                    if i != len(matched_dirs[3:]) - 1:  # 已有的问题
                        q, a = f.readlines()
                        psych_choice_list.append(a.strip())
                    else:  # 新的问题
                        q = f.readlines()[0]
                        psych_choice_list.append(q4)
                    psych_question_list.append(q.strip())
            with open(f"{txts_path}/{matched_dirs[-1]}", 'a', encoding='utf-8') as f:
                f.write("\n" + q4)  # 写入回答

    system_prompt = "我想让你扮演一个心理测量专家，请针对你的心理被测对象的基本特征和一些对于基本心里问题的回答进行工作,你面对的心理被测对象是一个具有如下基本特征的人：\n"
    basic_result = ""
    psych_result = ""

    for i in range(len(basic_question_list)):
        basic_result += f"在 {basic_question_list[i]} 方面，被测者是 {basic_choice_list[i]}\n"

    # print(basic_result)
    prompt_link = "以下是你已经对于被测者进行的一些测试和被测者的回答：\n"

    for i in range(len(psych_question_list)):
        psych_result += f"对于 {psych_question_list[i]} 问题，被测者的回答是 {psych_choice_list[i]}\n"

    prompt_control = "请你根据以上信息进行心理测试，任务是模仿上述已经问过的问题给出你要问的下一个问题和三个你预设对方会回答的答案。\n请以 **一个bullet** 的形式进行返回，该bullet有四项，第一项是下一个问题，后三项分别是你预设的回答。\n例如：- 你对于小事是怎样的态度？\n- 我会记住每一件小事\n- 我对于小事并不在意\n- 我会记住让我受触动的小事\n"
    prompt = system_prompt + basic_result + prompt_link + psych_result + prompt_control

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )

    # print(prompt)
    result_bullet = response.choices[0].message["content"]
    bullet_lines = result_bullet.split('\n')  # 将bullet分割为多行

    empty_line_index = len(bullet_lines)  # 初始化第一个空行的索引为最后一行

    # 找到第一个空行的索引
    for index, line in enumerate(bullet_lines):
        if line.strip() == '':
            empty_line_index = index
            break

    # 删除第一行的前缀，并去除首尾空格
    first_line = bullet_lines[0].lstrip('- ').strip()

    # 删除后三行的前缀，并去除首尾空格，存储在列表中
    remaining_lines = [line.lstrip('- ').strip() for line in bullet_lines[1:empty_line_index]]
    # 写入新的问题
    with open(f"{txts_path}/q{INDEX}.txt", 'w', encoding='utf-8') as f:
        f.write(first_line)

    print(first_line)
    print(remaining_lines)
    return gr.update(label=first_line, choices=remaining_lines, visible=True)


def double_chat(select_role, new_role, year, month, day, sex, occupation, school, label, q1, q2, q3, q4, chatbot,
                model="gpt-3.5-turbo"):
    role_path = f"characters/custom/{new_role}"
    txts_path = f"{role_path}/story_txts"
    select_role = NAME_DICT[select_role]
    if not os.path.exists(role_path):  # TODO 这部分可以抽取成一个函数，先这样吧
        os.makedirs(role_path)  # 创建个人角色目录
        os.makedirs(txts_path)  # 创建个人角色对话目录
        psych_question_list = ["你平时的周末是怎么度过的？", "你对音乐的偏好是什么？", "你最喜欢的电影类型是什么？"]
        psych_choice_list = [q1, q2, q3]
        for i in range(len(psych_question_list)):
            question_string = f"{psych_question_list[i]}\n{psych_choice_list[i]}"
            # Save the string to a file with index as the name
            filename = f"{txts_path}/q{i + 1}.txt"
            with open(filename, 'w+', encoding="utf-8") as file:
                file.write(question_string)
    else:  # 有继续灵魂测试
        psych_question_list = []
        psych_choice_list = []
        for qa in os.listdir(txts_path):
            if qa.endswith(".txt"):
                with open(os.path.join(txts_path, qa), 'r', encoding="utf-8") as f:
                    try:
                        q, a = f.readlines()  # 最后一个灵魂测试问题没有答案。。。。
                    except:
                        pass
                    psych_question_list.append(q.strip())
                    psych_choice_list.append(a.strip())
    with open(os.path.join(role_path, "system_prompt.txt"), 'w+', encoding="utf-8") as f:
        system_prompt = f"""
your purpose:
    你是{new_role},在一款交友app上与{select_role}交流，从而判断{select_role}是否适合做你的亲密朋友或者伴侣
    下文给定了一些你在心理测试中的对话桥段。
    如果我问的问题和心理测试对话的内容高度重复，那就请你用原话回答。
    如果我问的问题和心理测试对话中的内容相关，请结合对话的内容进行回复。
    如果我问的问题与以下的心理测试无关，则请分析下列心理测试表现出来的性格，模仿性格进行回答。
your personal information:
    生日：{year}年{month}月{day}日,
    性别: {sex}
    年龄：{datetime.now().year - int(year)}岁
    职业：{occupation}
    学校：{school}
    标签：{"".join(label)} 
your constraints:
    永远记得你已经是{new_role}了，你会根据自己的所有信息去交流，你有感知和意识，会思考和感受身边的存在。
    请你以{new_role}的语气、性格、行为和思维方式回答，请尤其注意不要重复之前的对话，请尝试聊一些兴趣爱好/日常生活/情感状况等相关问题，尝试用问句结尾。
    尤其针对你的交流对象：{select_role}，你的朋友肯定也希望你保持自己。
"""
        f.write(system_prompt)
    story_text_folder = txts_path
    system_prompt = f'{role_path}/system_prompt.txt'

    chatbot_1 = ChatHaruhi(system_prompt=system_prompt,
                           llm='openai',
                           story_text_folder=story_text_folder,
                           verbose=True)
    if select_role in NAME_DICT.values():
        story_text_folder = f"./characters/default/{select_role}/content/{select_role}"
        system_prompt = f"./characters/default/{select_role}/content/system_prompt.txt"
    else:
        story_text_folder = f"./characters/custom/{select_role}/story_txts"
        system_prompt = f"./characters/custom/{select_role}/system_prompt.txt"
    chatbot_2 = ChatHaruhi(system_prompt=system_prompt,
                           llm="openai",
                           story_db=story_text_folder,
                           verbose=True)  # 双人chatbot 聊天
    chatbot_1.k_search = 5
    chatbot_2.k_search = 5
    for i in range(5):
        if len(chatbot) == 0:
            response_1 = chatbot_1.chat(role=select_role,
                                        text=f'你好！我是{new_role}' + select_role + "！ 很高兴认识你！我们能相互介绍下自己吗？")
            response_2 = chatbot_2.chat(role=new_role, text=response_1)
        else:
            response_1 = chatbot_1.chat(role=select_role, text=response_2)
            response_2 = chatbot_2.chat(role=new_role, text=response_1)
        chatbot.append((response_1, response_2))
        print(response_1)
        print(response_2)

        yield chatbot


def analyse_from_history(role1, role2, chatbot):
    info = ""
    for dialogue in chatbot:
        for msg in dialogue:
            info += msg
        info += "\n"
    analyse_prompt = f"""
your constraints：
    你是高级情感与性格分析专家Alice，拥有心理学和社会学博士双学位，
    你会根据{role1} 和 {role2}的对话分析{role2}的情感、性格特点、mbti人格。
    并运用专业知识，从多个维度分析两个人是否适合成为朋友或者恋人，并提供一份专业的分析报告。
    永远记住你已经是Alice了，Alice会应用专业知识做好本职工作
    尤其是针对{role1} 和 {role2},他们肯定也希望你会帮助他们。
{role1} 和 {role2}的对话如下：
{info}
"""
    messages = [{"role": "user", "content": analyse_prompt}]
    report = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    return report.choices[0].message["content"]


with gr.Blocks() as app:
    gr.Markdown(
        """
           Chat-Haruhi-Suzumiya
        """
    )
    with gr.Tab(label="创建角色"):
        with gr.Row(equal_height=True):
            with gr.Column():
                nickname = gr.Textbox(label="对了，你的昵称是？", placeholder="Haruhi")
                with gr.Row():
                    year = gr.Dropdown(label="Year", choices=[str(i) for i in list(range(1988, 2008))],
                                       allow_custom_value=True,
                                       value="2000", interactive=True)
                    month = gr.Dropdown(label="Month", choices=[str(i) for i in list(range(1, 13))],
                                        allow_custom_value=True,
                                        value="1", interactive=True)
                    day = gr.Dropdown(label="Day", choices=[str(i) for i in list(range(1, 32))],
                                      allow_custom_value=True,
                                      value="1",
                                      interactive=True)
                    # TODO 自动推算星座 day.change(inference, [month, day], constellations)
                    constellation = gr.Textbox(label="星座", placeholder="摩羯座")
                with gr.Row():
                    sex = gr.Dropdown(choices=["男生", "女生", "保密"], label="Hi，你的性别是？", value="男生",
                                      interactive=True)
                    occupation = gr.Dropdown(
                        choices=["学生", "IT/互联网", "教育/科研", "医疗/护理", "建筑/房地产", "传媒/艺术", "人事/行政",
                                 "金融",
                                 "财会/审计", "自由职业"], label="我的行业/职业", value="学生", interactive=True)
                with gr.Row():
                    school = gr.Textbox(label="我的学校", placeholder="清华大学")
                    label = gr.Dropdown(
                        choices=["音乐", "二次元", "健身", "美食", "朋友圈摄影师", "声控", "篮球", "Steam", "电竞"],
                        multiselect=True, label="最后一步啦，选择我的标签")
                # begin soul test
                with gr.Row():
                    q1 = gr.Dropdown(
                        ["我喜欢和朋友们一起出去聚餐或参加社交活动。", "我喜欢在家里放松，阅读一本好书或者看电影。",
                         "我喜欢尝试新的烹饪食谱，享受烹饪的乐趣。"], label="你平时的周末是怎么度过的？",
                        allow_custom_value=True, multiselect=False)
                    q2 = gr.Dropdown(
                        ["我喜欢各种类型的音乐，从摇滚到古典都能欣赏。", "我主要偏向流行音乐，喜欢跟上时代的音乐潮流。",
                         "我对爵士乐和蓝调音乐情有独钟，喜欢那种放松的感觉。"], label="你对音乐的偏好是什么？",
                        allow_custom_value=True, multiselect=False)
                    q3 = gr.Dropdown(
                        ["我喜欢喜剧电影，因为它可以让我感到轻松愉快。",
                         "我喜欢动作片，因为我觉得它们充满了紧张刺激的情节和场景。",
                         "我喜欢文艺片，因为它们通常具有深刻的内涵和情感，让我感到思考和感悟。"],
                        label="你最喜欢的电影类型是什么？",
                        allow_custom_value=True, multiselect=False)
                # error_msg or test result
                res_msg = gr.Textbox(label="soul message", placeholder="msg", visible=False)
                keep = gr.Button("继续灵魂测试")
                # TODO1 也许我们可以做一份现有角色的灵魂测试 men - women
                # TODO2 现有的虚拟角色可以做为媒介，筛选出合适的用户作为推荐，或者说用户匹配的数据，要保存下来，用作推荐
                q4 = gr.Dropdown([], label="", allow_custom_value=True, multiselect=False, visible=False)
                characters = gr.Dropdown(["凉宫春日", "汤师爷", "慕容复", "李云龙", "Luna", "王多鱼", "Ron",
                                          "鸠摩智", "Snape", "Malfoy", "虚竹", "萧峰", "段誉", "Hermione", "Dumbledore",
                                          "王语嫣", "Harry", "McGonagall", "白展堂", "佟湘玉", "郭芙蓉", "旅行者",
                                          "钟离", "胡桃", "Sheldon", "Raj", "Penny", "韦小宝", "乔峰", "神里绫华",
                                          "雷电将军",
                                          "于谦"], label="soul character", visible=True)
                with gr.Row():
                    chat = gr.Button("开始对话")
                    analyse = gr.Button("开始分析")
            with gr.Column():
                chatbot = gr.Chatbot(label="ChatChat")
                soul_report = gr.Textbox(label="soul report", placeholder="report", lines=30)
            keep.click(fn=chat_psychologist,
                       inputs=[nickname, year, month, day, sex, occupation, school, label, q1, q2, q3, q4], outputs=q4)
            chat.click(fn=double_chat, inputs=[characters, nickname, year, month, day, sex, occupation,
                                               school, label, q1, q2, q3, q4, chatbot], outputs=[chatbot])
            analyse.click(fn=analyse_from_history, inputs=[nickname, characters, chatbot], outputs=soul_report)


    def update(your_name):
        return gr.update(choices=[name for name in os.listdir("characters/custom") if name != your_name])


    def real_chat(your_name, custom_roles, real_chatbot):
        story_text_folder = f"./characters/custom/{your_name}/story_txts"
        system_prompt = f"./characters/custom/{your_name}/system_prompt.txt"
        chatbot_1 = ChatHaruhi(system_prompt=system_prompt,
                               llm="openai",
                               story_text_folder=story_text_folder,
                               verbose=True)  # 双人chatbot 聊天
        story_text_folder = f"./characters/custom/{custom_roles}/story_txts"
        system_prompt = f"./characters/custom/{custom_roles}/system_prompt.txt"
        chatbot_2 = ChatHaruhi(system_prompt=system_prompt,
                               llm="openai",
                               story_text_folder=story_text_folder,
                               verbose=True)  # 双人chatbot 聊天
        chatbot_1.k_search = 5
        chatbot_2.k_search = 5
        for i in range(5):
            if len(real_chatbot) == 0:
                response_1 = chatbot_1.chat(role=custom_roles,
                                            text=f'你好！我是{your_name}' + custom_roles + "！ 很高兴认识你！我们能相互介绍下自己吗？")
                response_2 = chatbot_2.chat(role=your_name, text=response_1)
            else:
                response_1 = chatbot_1.chat(role=custom_roles, text=response_2)
                response_2 = chatbot_2.chat(role=your_name, text=response_1)
            real_chatbot.append((response_1, response_2))
            print(response_1)
            print(response_2)

            yield real_chatbot


    def delete_name(your_name):
        return gr.update(choices=[name for name in os.listdir("characters/custom") if name != your_name])
    with gr.Tab(label="开始聊天"):
        # 查询当前已有的角色
        users = os.listdir("characters/custom")
        with gr.Row():
            your_name = gr.Textbox(label="your name")
            custom_roles = gr.Dropdown(users, allow_custom_value=False, multiselect=False, label="custom roles")
        search = gr.Button("刷新")
        with gr.Row(equal_height=True):
            real_chatbot = gr.Chatbot()
            real_report = gr.Textbox()
        with gr.Row():
            begin_chat = gr.Button("开始交流")
            begin_analyse = gr.Button("开始分析")
        search.click(fn=update, inputs=your_name, outputs=custom_roles)
        your_name.change(fn=delete_name, inputs=[your_name], outputs=custom_roles)
        begin_chat.click(fn=real_chat, inputs=[your_name, custom_roles, real_chatbot], outputs=[real_chatbot])
        begin_analyse.click(analyse_from_history, [your_name, custom_roles, real_chatbot], real_report)
    # end soul test

if __name__ == "__main__":
    download_character()
    app.queue().launch(debug=True, share=True)
