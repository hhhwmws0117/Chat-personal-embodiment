# bala bala 

# TODO
- [x] 继续灵魂测试
- [x] 基础的gradio
- [x] 继续灵魂测试接入正常
- [x] 根据已知信息生成prompt
      粗暴一点，先保存在txt吧，hhhh
- [x] 先聊上，再考虑存储
- [x] 接入soul test, gradio启动时，下载所有chromadb，选中角色后，生成新建角色的system_prompt, 开启双人对话
- [x] 接入analysis_from_history
- [ ] 接入store_file_standard
- [ ] 如果多次灵魂测试把之前的灵魂测试放进prompt，
      继续灵魂测试会把q1，q2，q3，存入story_txts中。
      double_chat 不用传入直接从story_txts中读取, 新的q4要保存
- [ ] 实时更新新创建的角色 ，查询角色按钮
- [ ] 聊天记录的保存


role1 personal information:
  生日：
  职业：
  学校：
  标签： 
role1 personal hobby 
  q1 
  q2
  q3 
role2 personal information:
  生日：
  职业：
  学校： 
  标签：
role2 personal hobby 
  q1 
  q2 
  q3
role1,role2 chat history
  role1:xxx
  role2:xxx
  ...
system_prompt2 with character
  ```
  你是一名专业的情感与性格分析师，你将根据我提供的两位角色的信息，分析他们的情感、
  性格特点、mbti人格。并从多个维度分析两个人是否有可能成为朋友或者恋人。
  信息如下：
  {chat_history}
  ```
  system_prompt1 with user:
  ```
  你是一名专业的情感与性格分析师，你将根据我提供的两位角色的信息，分析他们的情感、
  性格特点、mbti人格。并从多个维度分析两个人是否有可能成为朋友或者恋人。
  信息如下：
  {info}
  ```
  
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