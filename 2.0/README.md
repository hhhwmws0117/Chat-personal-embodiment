# bala bala 

# TODO
- [x] 继续灵魂测试
- [x] 基础的gradio
- [x] 继续灵魂测试接入正常
- [ ] 根据已知信息生成prompt
      粗暴一点，先保存在txt吧，hhhh
- [ ] 接入soul test, gradio启动时，下载所有chromadb，选中角色后，生成新建角色的system_prompt, 开启双人对话
- [ ] 接入analysis_from_history
- [ ] 接入store_file_standard
- [ ] 实时更新新创建的角色


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
