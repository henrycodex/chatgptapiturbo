import gradio as gr
import os 
import json 
import requests
import config as config

api_key = config.OPENAI_API_KEY

#Streaming endpoint
API_URL = "https://api.openai.com/v1/chat/completions" #os.getenv("API_URL") + "/generate_stream"

#Testing with my Open AI Key 
#openai_api_key = os.getenv("open_api_key") 

def predict(inputs, top_p, temperature, chat_counter, chatbot=[], history=[]):  #repetition_penalty, top_k

    payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": f"{inputs}"}],
    "temperature" : 1.0,
    "top_p":1.0,
    "n" : 1,
    "stream": True,
    "presence_penalty":0,
    "frequency_penalty":0,
    }

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    print(f"chat_counter - {chat_counter}")
    if chat_counter != 0 :
        messages=[]
        for data in chatbot:
          temp1 = {}
          temp1["role"] = "user" 
          temp1["content"] = data[0] 
          temp2 = {}
          temp2["role"] = "assistant" 
          temp2["content"] = data[1]
          messages.append(temp1)
          messages.append(temp2)
        temp3 = {}
        temp3["role"] = "user" 
        temp3["content"] = inputs
        messages.append(temp3)
        #messages
        payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages, #[{"role": "user", "content": f"{inputs}"}],
        "temperature" : temperature, #1.0,
        "top_p": top_p, #1.0,
        "n" : 1,
        "stream": True,
        "presence_penalty":0,
        "frequency_penalty":0,
        }

    chat_counter+=1

    history.append(inputs)
    print(f"payload is - {payload}")
    # make a POST request to the API endpoint using the requests.post method, passing in stream=True
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    #response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    token_counter = 0 
    partial_words = "" 

    counter=0
    for chunk in response.iter_lines():
        if counter == 0:
          counter+=1
          continue
        counter+=1
        # check whether each line is non-empty
        if chunk :
          # decode each line as response data is in bytes
          if len(json.loads(chunk.decode()[6:])['choices'][0]["delta"]) == 0:
            break
          #print(json.loads(chunk.decode()[6:])['choices'][0]["delta"]["content"])
          partial_words = partial_words + json.loads(chunk.decode()[6:])['choices'][0]["delta"]["content"]
          if token_counter == 0:
            history.append(" " + partial_words)
          else:
            history[-1] = partial_words
          chat = [(history[i], history[i + 1]) for i in range(0, len(history) - 1, 2) ]  # convert to tuples of list
          token_counter+=1
          yield chat, history, chat_counter  # resembles {chatbot: chat, state: history}  
        
       

def reset_textbox():
    return gr.update(value='')

title = """<h2 align="center">????ChatGPT Turbo API 3.5????</h2>"""
description = """The following is a conversation between a human and AI system named ChatGPT.
This is the most recently updated ChatGPT API 3.5 GPT Turbo"""
                
with gr.Blocks(css = """#col_container {width: 700px; margin-left: auto; margin-right: auto;}
                #chatbot {height: 400px; overflow: auto;}""") as demo:
    gr.HTML(title)
    gr.HTML('''<center><a href=""><img src="" alt=""></a></center>''')
    with gr.Column(elem_id = "col_container"):
        chatbot = gr.Chatbot(elem_id='chatbot') #c
        inputs = gr.Textbox(placeholder= "Hello! You can speak to ChatGPT about anything thats on your mind.", label= "ChatGPT 3.5 Turbo API") #t
        state = gr.State([]) #s
        b1 = gr.Button()
    
        #inputs, top_p, temperature, top_k, repetition_penalty
        with gr.Accordion("Advanced Settings", open=False):
            top_p = gr.Slider( minimum=0.1, maximum=1.0, value=1.0, step=0.01, interactive=True, label="Top-p (nucleus sampling)",)
            temperature = gr.Slider( minimum=0.1, maximum=1.0, value=1.0, step=0.1, interactive=True, label="Temperature",)
            top_k = gr.Slider( minimum=1, maximum=50, value=4, step=1, interactive=True, label="Top-k",)
            repetition_penalty = gr.Slider( minimum=0.1, maximum=3.0, value=1.03, step=0.01, interactive=True, label="Repetition Penalty", )
            chat_counter = gr.Number(value=0, visible=False, precision=0)

    inputs.submit( predict, [inputs, top_p, temperature, chat_counter, chatbot, state], [chatbot, state, chat_counter],)
    b1.click( predict, [inputs, top_p, temperature, chat_counter, chatbot, state], [chatbot, state, chat_counter],)
    b1.click(reset_textbox, [], [inputs])
    inputs.submit(reset_textbox, [], [inputs])
                    
    #gr.Markdown(description)
    demo.queue().launch(debug=True)
