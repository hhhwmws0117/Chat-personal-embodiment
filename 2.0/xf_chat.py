import os

from chatharuhi import ChatHaruhi
import openai

openai.api_key = "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"
chatbot = ChatHaruhi.chat("hello")
print(chatbot)