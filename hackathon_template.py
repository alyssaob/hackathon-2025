import json
import os
from datetime import date
import re
from pydantic import BaseModel
from fastapi import FastAPI
from gtts import gTTS

from api import plaid_call
from api import gemini_call
from graphs import make_bar_chart
from graphs import make_histogram
from graphs import make_pie_chart
from fastapi.middleware.cors import CORSMiddleware

def decode_json(json_string):
    return json.loads(json_string)


def make_json(user_id, gemini_result):

    output = {"userId": user_id, "conversation": gemini_result}
    json_str = json.dumps(output)
    return json_str

def parse_gemini(gemini_result):
    gemini_result = gemini_result.strip()
    gemini_result = re.sub(r"^```json\s*|\s*```$", "", gemini_result)
    return json.loads(gemini_result)

def texttospeech(text):
# Text you want to convert to speech
    language = 'en'
    tts = gTTS(text=text, lang=language, slow=False)
    file_path = "output.mp3"
    tts.save(file_path)
    print (file_path)
    return file_path



def chatbot(json_string, user_id):
    user_input = json.loads(json_string)
    print(type(user_input))
    print(user_input)
    user_input = user_input["messages"]
    # user_input = "How much did I spend in each spending category last month?"
    plaid_dictionary = plaid_call(user_id)
    gemini_result = gemini_call(user_input, plaid_dictionary)
    gemini_result_dict = parse_gemini(gemini_result)
    output = {}
    output["userId"] = user_id
    # output["messages"] = {"output_paragraph": gemini_result_dict["output_prompt"]}
    output["messages"] = gemini_result_dict["output_prompt"]
    # texttospeech(gemini_result_dict["output_prompt"])

    if gemini_result_dict["answer_flag"]:
         transaction_data = gemini_result_dict["category_list"]
         graph_type = gemini_result_dict["graph"]
         if graph_type == "Bar chart":
             output["conversation"]["graph"] = make_bar_chart(transaction_data)
         elif graph_type == "Pie chart":
             output["conversation"]["graph"] = make_pie_chart(transaction_data)
         elif graph_type == "Histogram":
            output["conversation"]["graph"] = make_histogram(transaction_data)
     else:
    #     output["conversation"]["graph"] = "none"
    print(output)
    print(json.dumps(output))
    return output
    # return json.dumps(output)

# chat_response = chatbot("","ins_109511")
# print(chat_response)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- you can restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}

@app.get("/")
def test():
    return {"status": "ok"}


@app.post("/chatbot-response")
def process_text(payload):
    # chat_response = chatbot(payload, "ins_109511")
    chat_response = {"userId": "ins_109511", "messages": "It looks like your spending in November was a bit higher than in December, and there are a few areas where you might be able to trim down. In November, you spent 500.0 on KFC and 500.0 on Madison Bicycle Shop. While these are significant purchases, if they aren't essential, they could be areas to cut back. Additionally, your Uber rides in November totaled 6.33, which is slightly more than your December Uber spending of 5.4. Small, recurring expenses like these can add up, so reducing them could help you save. If you're looking to save this month, consider pausing non-essential shopping trips or looking for ways to reduce your transportation costs."}
    return chat_response

@app.post("/chatbot-real")
def process_text(payload):
    print(payload)
    chat_response = chatbot(payload, "ins_109511")
    return chat_response

# @app.get("/chatbot-response")
# def call_chat():
#     chat_response = chatbot("","ins_109511")
#     return chat_response




