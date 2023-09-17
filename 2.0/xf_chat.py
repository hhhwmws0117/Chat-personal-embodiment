def chat_psychologist(system_prompt, basic_question_list, basic_choice_list, psych_question_list, psych_choice_list, model="gpt-3.5-turbo", dialogue_example = ""):
  """
  :param system_prompt:
  :param basic_question_list:
  :param basic_choice_list:
  :param psych_question_list:
  :param psych_choice_list:
  :param model:
  :param dialogue_example:
  :return: QA
  """
  # basic_choice_list = ["回答1", "回答2", "回答3"]
  # basic_question_list = ["问题1", "问题2", "问题3"]
  # system_prompt = "我想让你扮演一个心理测量专家，请针对你的心理被测对象的基本特征和一些对于基本心里问题的回答进行工作,你面对的心理被测对象是一个具有如下基本特征的人：\n"
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

  return first_line, remaining_lines