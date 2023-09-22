import time

import gradio as gr

def say(a):
    for i in list(a):
        time.sleep(0.2)
        yield i


with gr.Blocks() as app:
    a = gr.Textbox()
    b = gr.Textbox()
    btn = gr.Button()
    btn.click(fn=say, inputs=a, outputs=b)

app.queue().launch(debug=True, share=True)