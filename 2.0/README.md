# bala bala 
# 文件夹命名规范
- 虚拟角色，characters/default
- 自定义角色 
  - 主目录 characters/custom/nickname
  - story 目录 characters/custom/nickname/story_txts
  - qa 命名规范，q1.txt, q2.txt, q3.txt,....
    - 使用正则表达式匹配，story_txts中有几个qa问题了，新的qa命名为 f"q{match_number+1}.txt"，且在继续灵魂测试时
    - 创建该文件，写入新的灵魂测试的问题，在继续灵魂测试也要去从story_txts中去读取。
    - double_chat 时，要把用户选择的新的灵魂测试答案写入匹配的最后一个文件中。
# TODO
- [x] 继续灵魂测试
- [x] 基础的gradio
- [x] 继续灵魂测试接入正常
- [x] 根据已知信息生成prompt
      粗暴一点，先保存在txt吧，hhhh
- [x] 先聊上，再考虑存储
- [x] 接入soul test, gradio启动时，下载所有chromadb，选中角色后，生成新建角色的system_prompt, 开启双人对话
- [x] 接入analysis_from_history
- [x] system_prompt 中不需要qa，会和shot data 重复
- [x] 第一个tab用于创建和测试角色，且chatbot和 soul report 要分开
- [ ] 第二个tab用于chat
- [x] 如果多次灵魂测试把之前的灵魂测试放进继续灵魂测试的prompt，
      问题命名规范，q1.txt, q2.txt, q3.txt, 
- [ ] 实时更新新创建的角色 ，查询角色按钮
- [ ] 聊天记录的保存
- [ ] 自动计算星座
- [ ] 写一个constants.py 保存常量
- [ ] 接入讯飞
- [ ] 参数校验，error_msg 
  
- 渐进式数字个人化身的塑造
  - 从用户和chatbot聊天的对话中抽取
  - 从用户和用户的聊天中抽取对话 作为story
  - 支持识别纸质文字，形成个人story
  - 各个平台的文本导出
  - messages = chat_history + system_prompt + story + q

- 逻辑
  - username 限制，如果重复则提示
  - 先填表
  - 开始聊天
  - 分析，给出报告
  - 