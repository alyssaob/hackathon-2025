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
             output["imageData"] = make_bar_chart(transaction_data)
         elif graph_type == "Pie chart":
             output["imageData"] = make_pie_chart(transaction_data)
         elif graph_type == "Histogram":
            output["imageData"] = make_histogram(transaction_data)
    # else:
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
    chat_response = {"userId": "ins_109511", "messages": "Looking at your recent transactions, I see a few areas where you might be able to trim some spending this month. Your \"Food & Dining\" category shows a total of 20.73, primarily from Starbucks and McDonald's. If you're looking to save, reducing these small, frequent purchases could make a difference. Additionally, your \"Shopping\" category for this period is 500.0. If this is for a specific item, you might consider if it's a necessary purchase right now or if there's a more budget-friendly alternative. Another area to consider is \"Auto & Transport\" with a few Uber rides totaling 16.73. Could any of these trips be replaced with walking or public transport? \n\nHere's a potential plan to cut spending:\n\n*   **Reduce Dining Out:** Aim to cut your \"Food & Dining\" spending by half this month. Try packing lunches or making coffee at home more often.\n*   **Re-evaluate \"Shopping\" Purchases:** For your 500.0 \"Shopping\" transaction, consider if it's a need or a want. If it's a want, try waiting 30 days to see if you still feel the same way. If it's a need, look for sales or discounts.\n*   **Optimize Transportation:** For your \"Auto & Transport\" expenses, see if you can consolidate trips or opt for more affordable modes of transport for shorter distances.\n\nBy making small adjustments in these areas, you can effectively reduce your overall spending.", "imageData": "{\"data\":[{\"hovertemplate\":\"Category=%{x}\\u003cbr\\u003eAmount ($)=%{text}\\u003cextra\\u003e\\u003c\\u002fextra\\u003e\",\"legendgroup\":\"\",\"marker\":{\"color\":\"#636efa\",\"pattern\":{\"shape\":\"\"}},\"name\":\"\",\"orientation\":\"v\",\"showlegend\":false,\"text\":{\"dtype\":\"f8\",\"bdata\":\"4noUrkchMUAAAAAAAD2gQAAAAAAAoGNACtejcD3mn0DhehSuR6WAQAAAAAAAQH9AZmZmZmY2hUAAAAAAAEB\\u002fwA==\"},\"textposition\":\"outside\",\"x\":[\"Auto & Transport\",\"Bills & Utilities\",\"Entertainment\",\"Financial\",\"Food & Dining\",\"Other\",\"Shopping\",\"Travel\"],\"xaxis\":\"x\",\"y\":{\"dtype\":\"f8\",\"bdata\":\"4noUrkchMUAAAAAAAD2gQAAAAAAAoGNACtejcD3mn0DhehSuR6WAQAAAAAAAQH9AZmZmZmY2hUAAAAAAAEB\\u002fwA==\"},\"yaxis\":\"y\",\"type\":\"bar\",\"texttemplate\":\"$%{text:.2f}\"}],\"layout\":{\"template\":{\"data\":{\"histogram2dcontour\":[{\"type\":\"histogram2dcontour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"choropleth\":[{\"type\":\"choropleth\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"histogram2d\":[{\"type\":\"histogram2d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"heatmap\":[{\"type\":\"heatmap\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"contourcarpet\":[{\"type\":\"contourcarpet\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"contour\":[{\"type\":\"contour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"surface\":[{\"type\":\"surface\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"mesh3d\":[{\"type\":\"mesh3d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"scatter\":[{\"fillpattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2},\"type\":\"scatter\"}],\"parcoords\":[{\"type\":\"parcoords\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolargl\":[{\"type\":\"scatterpolargl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"bar\":[{\"error_x\":{\"color\":\"#2a3f5f\"},\"error_y\":{\"color\":\"#2a3f5f\"},\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"bar\"}],\"scattergeo\":[{\"type\":\"scattergeo\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolar\":[{\"type\":\"scatterpolar\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"histogram\":[{\"marker\":{\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"histogram\"}],\"scattergl\":[{\"type\":\"scattergl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatter3d\":[{\"type\":\"scatter3d\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermap\":[{\"type\":\"scattermap\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermapbox\":[{\"type\":\"scattermapbox\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterternary\":[{\"type\":\"scatterternary\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattercarpet\":[{\"type\":\"scattercarpet\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"carpet\":[{\"aaxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"baxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"type\":\"carpet\"}],\"table\":[{\"cells\":{\"fill\":{\"color\":\"#EBF0F8\"},\"line\":{\"color\":\"white\"}},\"header\":{\"fill\":{\"color\":\"#C8D4E3\"},\"line\":{\"color\":\"white\"}},\"type\":\"table\"}],\"barpolar\":[{\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"barpolar\"}],\"pie\":[{\"automargin\":true,\"type\":\"pie\"}]},\"layout\":{\"autotypenumbers\":\"strict\",\"colorway\":[\"#636efa\",\"#EF553B\",\"#00cc96\",\"#ab63fa\",\"#FFA15A\",\"#19d3f3\",\"#FF6692\",\"#B6E880\",\"#FF97FF\",\"#FECB52\"],\"font\":{\"color\":\"#2a3f5f\"},\"hovermode\":\"closest\",\"hoverlabel\":{\"align\":\"left\"},\"paper_bgcolor\":\"white\",\"plot_bgcolor\":\"#E5ECF6\",\"polar\":{\"bgcolor\":\"#E5ECF6\",\"angularaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"radialaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"ternary\":{\"bgcolor\":\"#E5ECF6\",\"aaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"baxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"caxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"coloraxis\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"colorscale\":{\"sequential\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"sequentialminus\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"diverging\":[[0,\"#8e0152\"],[0.1,\"#c51b7d\"],[0.2,\"#de77ae\"],[0.3,\"#f1b6da\"],[0.4,\"#fde0ef\"],[0.5,\"#f7f7f7\"],[0.6,\"#e6f5d0\"],[0.7,\"#b8e186\"],[0.8,\"#7fbc41\"],[0.9,\"#4d9221\"],[1,\"#276419\"]]},\"xaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"yaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"scene\":{\"xaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"yaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"zaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2}},\"shapedefaults\":{\"line\":{\"color\":\"#2a3f5f\"}},\"annotationdefaults\":{\"arrowcolor\":\"#2a3f5f\",\"arrowhead\":0,\"arrowwidth\":1},\"geo\":{\"bgcolor\":\"white\",\"landcolor\":\"#E5ECF6\",\"subunitcolor\":\"white\",\"showland\":true,\"showlakes\":true,\"lakecolor\":\"white\"},\"title\":{\"x\":0.05},\"mapbox\":{\"style\":\"light\"}}},\"xaxis\":{\"anchor\":\"y\",\"domain\":[0.0,1.0],\"title\":{\"text\":\"Category\"}},\"yaxis\":{\"anchor\":\"x\",\"domain\":[0.0,1.0],\"title\":{\"text\":\"Amount ($)\"},\"tickprefix\":\"$\",\"tickformat\":\",.2f\"},\"legend\":{\"tracegroupgap\":0},\"title\":{\"text\":\"Total Amount by Category\"},\"barmode\":\"relative\",\"margin\":{\"l\":40,\"r\":20,\"t\":60,\"b\":80},\"bargap\":0.35}}"}
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






