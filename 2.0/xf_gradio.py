from chatharuhi import ChatHaruhi
import zipfile
import os
import requests
import gradio as gr
import openai

openai.api_key = "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"

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
            destination_folder = f"characters/{ai_role_en}"
            with zipfile.ZipFile(destination_file, 'r') as zip_ref:
                zip_ref.extractall(destination_folder)
        db_folder = f"./characters/{ai_role_en}/content/{ai_role_en}"
        system_prompt = f"./characters/{ai_role_en}/content/system_prompt.txt"
        ai_roles_obj[ai_role_en] = ChatHaruhi(system_prompt=system_prompt,
                                              llm="openai",
                                              story_db=db_folder,
                                              verbose=True)
    return ai_role_en

def chat_psychologist(nickname, year, month, day, sex, occupation, school, label, q1, q2, q3, q4, model="gpt-3.5-turbo",
                      dialogue_example=""):
    basic_question_list = ["昵称", "生日", "性别", "职业", "学校", "标签"]
    basic_choice_list = [nickname, f"{year}年{month}月{day}", sex, occupation, school, label]
    psych_question_list = ["你平时的周末是怎么度过的？", "你对音乐的偏好是什么？", "你最喜欢的电影类型是什么？"]
    psych_choice_list = [q1, q2, q3]
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
    print(first_line)
    print(remaining_lines)
    return gr.update(label=first_line, choices=remaining_lines, visible=True)

def double_chat():
    pass

with gr.Blocks() as app:
    gr.Markdown(
        """
           Chat-Haruhi-Suzumiya
        """
    )
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
                day = gr.Dropdown(label="Day", choices=[str(i) for i in list(range(1, 32))], allow_custom_value=True,
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
            """
            {'汤师爷': 'tangshiye', '慕容复': 'murongfu', '李云龙': 'liyunlong', 'Luna': 'Luna', '王多鱼': 'wangduoyu',
            'Ron': 'Ron', '鸠摩智': 'jiumozhi', 'Snape': 'Snape',
            '凉宫春日': 'haruhi', 'Malfoy': 'Malfoy', '虚竹': 'xuzhu', '萧峰': 'xiaofeng', '段誉': 'duanyu',
            'Hermione': 'Hermione', 'Dumbledore': 'Dumbledore', '王语嫣': 'wangyuyan',
            'Harry': 'Harry', 'McGonagall': 'McGonagall', '白展堂': 'baizhantang', '佟湘玉': 'tongxiangyu',
            '郭芙蓉': 'guofurong', '旅行者': 'wanderer', '钟离': 'zhongli',
            '胡桃': 'hutao', 'Sheldon': 'Sheldon', 'Raj': 'Raj', 'Penny': 'Penny', '韦小宝': 'weixiaobao',
            '乔峰': 'qiaofeng', '神里绫华': 'ayaka', '雷电将军': 'raidenShogun', '于谦': 'yuqian'}
            """
            with gr.Row():
                chat = gr.Button("提交灵魂测试")
        chatbot = gr.Chatbot()
        soul_report = gr.Textbox(label="soul report", placeholder="report", lines=30)
        keep.click(fn=chat_psychologist,
                   inputs=[nickname, year, month, day, sex, occupation, school, label, q1, q2, q3, q4], outputs=q4)
        chat.click(fn=double_chat, inputs=[])
    # end soul test


if __name__ == "__main__":
    app.launch(debug=True)
