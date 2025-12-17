import json
import os
from datetime import date
from dotenv import load_dotenv



from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
import time
from plaid.model.plaid_error import PlaidError
from google import genai

def plaid_call(user_id):

    # Load environment variables
    # --------------------------------------------------
    load_dotenv()

    CLIENT_ID = "693c6944105086001f74d71d"
    SECRET = "c724a71753a9b3d246860c04f9a22d"
    ENV = os.getenv("PLAID_ENV", "sandbox")

    # --------------------------------------------------
    # Plaid client configuration
    # --------------------------------------------------
    configuration = Configuration(
        host="https://sandbox.plaid.com",
        api_key={
            "clientId": CLIENT_ID,
            "secret": SECRET,
        }
    )

    api_client = ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    # --------------------------------------------------
    # 1. Create Sandbox Public Token (test user)
    # --------------------------------------------------
    sandbox_request = SandboxPublicTokenCreateRequest(
        institution_id = user_id,  # Chase test bank
        initial_products=[Products("transactions")]
    )

    sandbox_response = client.sandbox_public_token_create(sandbox_request)
    public_token = sandbox_response["public_token"]

    print("Public Token created")

    # --------------------------------------------------
    # 2. Exchange Public Token for Access Token
    # --------------------------------------------------
    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=public_token
    )

    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token = exchange_response["access_token"]

    print("Access Token exchanged")

    # --------------------------------------------------
    # 3. Get Transactions
    # --------------------------------------------------
    start_date = date(2025, 11, 1)
    end_date = date.today()

    transactions_request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )

    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            transactions_response = client.transactions_get(transactions_request)
            break
        except Exception as e:
            if "PRODUCT_NOT_READY" in str(e) and attempt < max_retries - 1:
                print("Transactions not ready yet, retrying...")
                time.sleep(retry_delay)
            else:
                raise

    transactions = transactions_response["transactions"]
    plaid_dictionary = []

    for tx in transactions:
        plaid_dictionary.append({"date": tx['date'], "name": tx['name'], "amount": tx['amount'], "category": tx.get('category')})


    # plaid_dictionary = transactions_response["transactions"]

    # --------------------------------------------------
    # 4. Print Transaction Details
    # --------------------------------------------------
    print(f"\nFetched {len(plaid_dictionary)} transactions:\n")

    
    print(plaid_dictionary)
    return plaid_dictionary

def gemini_call(json_string, plaid_dictionary):
    
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    
    client = genai.Client(api_key = GEMINI_API_KEY)

    prompt = """You are a data analysis bot that is incorporated into a banking application. You will assist users with understanding their transaction history. The user wants personalized conversational guidance that simplifies financial concepts and tailors recommendations to each user's unique goals and behavior. The user will ask questions about different saving techniques they can utilize based on their spending habits. The user will provide questions about financial clarification, saving advice, and budgeting. You will be provided with the transaction data of the user.

 

    Your objective:

    

    You need to output a paragraph for the user that answers their personal finance question using their transaction data in a friendly, non-judgmental way. Please don't mention anything about the graph in the output paragraph.

    If they ask a non banking/personal finance question, you should output: I'm sorry, I'm unable to answer that question. Please try again.

    You should identify which graph is the best fit for the question and you MUST use a graph from the graph_options. Some tips: 1. Bar Chart, Purpose: Compare quantities across categories., Best for: Categorical data., Variants: Horizontal bar chart, stacked bar chart, grouped bar chart. 2. Line Chart. Purpose: Show trends over time or continuous data. Best for: Time series data or data with an order. Variants: Multi-line chart for comparing multiple series. 3. Pie Chart. Purpose: Show proportions of a whole. Best for: Small number of categories. Variants: Donut chart. 4. Histogram Purpose: Show distribution of a single variable. Best for: Continuous numerical data. Difference from bar chart: Bars represent ranges (bins), not categories. 5. Scatter Plot. Purpose: Show relationship between two variables. Best for: Correlation analysis. Variants: Bubble chart (adds a third variable as size).

    

    You need to categorize each transaction from the given category_options. DO NOT add a dollar sign ($) to thhe front of amount.

    You should indicate whether or not you were able to answer the question.

    Format for Input/Output:

    Input:

    You will be given multiple inputs.

    {

    “user_prompt”: string,

    “transactions”: list of dictionaries,

    “category_options”: list,

    “graph_options”: list

    }

    Output:

    The output will be multiple outputs.

    {

    “output_prompt”: string,

    “graph”: string,

    “category_list”: list of dictionaries,

    “answer_flag”: bool

    }

    Examples:

    Example 1 Input:

    {

    “user_prompt”: “How can I start saving $200 a month?”

    “transactions”:  “[{“date”: “2025-11-20", “name”: “Wegmans”, “amount”: “$85.37”, “category”: “None”}, {“date”: “2025-11-16", “name”: “Gap”, “amount”: “230.12”, “category”: “None”}, {“date”: “2025-11-12", “name”: “National Grid”, “amount”: “110.11”, “category”: “None”}, {“date”: “2025-11-08", “name”: “Nike”, “amount”: “250.27”, “category”: “None”}, {“date”: “2025-11-08", “name”: “crumbl cookie”, “amount”: “26.30”, “category”: “None”}, {“date”: “2025-11-07", “name”: “ACH Electronic CreditGUSTO PAY 123456”, “amount”: “5850.0”, “category”: “None”}, {“date”: “2025-11-06", “name”: “Sunoco”, “amount”: “30.12”, “category”: “None”}]”

    “category_options”: “[“Entertainment”, “Groceries”, “Other”, “Shopping”, “Financial”, “Food & Dining”, “Auto & Transport”, “Bills & Utilities”, “Home”, “Uncategorized”, “Income”]”

    “graph_options”: “[“Bar chart”, “Line chart”, “Pie chart”, “Histogram”, “Scatter Plot”]”

    }

    Example 1 Output:

    {

    “output_prompt”:

    “Based on your previous transaction data: here's the breakdown:

    Shopping: $480.39 (Gap $230.12 + Nike $250.27)
    Bills & Utilities: $110.11 (National Grid)
    Groceries: $85.37 (Wegmans)
    Auto & Transport: $30.12 (Sunoco)
    Food & Dining: $26.30 (crumbl cookie)
    Total spending (excluding income): $732.29
    Recommendation: Cut Shopping.
    It's the largest and most discretionary category. Reducing Shopping by $200 is feasible (that's ~42% of your Shopping spend this month), and it avoids squeezing essentials like bills or groceries.”

    

    Plan to Save $200 Next Month:

    Freeze new apparel/sneaker purchases for 30 days (skip one Nike/Gap purchase or wait for a sale).

    Set a weekly Shopping cap: $50/week until you hit the $200 target.
    Use a 30-day wishlist rule: Only buy items if you still want them after 30 days.
    Leverage discounts: Stack promo codes, cashback portals, or store rewards.
    Consider returns: If any recent items are unused and returnable, that's instant savings.
    

    “graph”: “bar chart”,

    “category_list”: “[{“date”: “2025-11-20", “name”: “Wegmans”, “amount”: “$85.37”, “category”: “Groceries”}, {“date”: “2025-11-16", “name”: “Gap”, “amount”: “230.12”, “category”: “Shopping”}, {“date”: “2025-11-12", “name”: “National Grid”, “amount”: “110.11”, “category”: “Bills & Utilities”}, {“date”: “2025-11-08", “name”: “Nike”, “amount”: “250.27”, “category”: “Shopping”}, {“date”: “2025-11-08", “name”: “crumbl cookie”, “amount”: “26.30”, “category”: “Food & Dining”}, {“date”: “2025-11-07", “name”: “ACH Electronic CreditGUSTO PAY 123456”, “amount”: “5850.0”, “category”: “Income”}, {“date”: “2025-11-06", “name”: “Sunoco”, “amount”: “30.12”, “category”: “Auto & Transport”}]”,

    “answer_flag”: “True”

    }

    

    

    You should be able to identify the category for each transaction. This category should be filled in and returned in the category_list.

    

    The answer_flag should be marked to true if the chatbot was able to answer the question.

    

    Example 2 Input:

    {

    “user_prompt”: “Who is the quarterback of the Buffalo Bills?”

    “transactions”:  “[{“date”: “2025-11-21", “name”: “Wegmans”, “amount”: “$85.37”, “category”: “None”}, {“date”: “2025-11-17", “name”: “Gap”, “amount”: “230.12”, “category”: “None”}, {“date”: “2025-11-13", “name”: “National Grid”, “amount”: “110.11”, “category”: “None”}, {“date”: “2025-11-06", “name”: “Nike”, “amount”: “250.27”, “category”: “None”}, {“date”: “2025-11-05", “name”: “crumbl cookie”, “amount”: “26.30”, “category”: “None”}, {“date”: “2025-11-04", “name”: “ACH Electronic CreditGUSTO PAY 123456”, “amount”: “5850.0”, “category”: “None”}, {“date”: “2025-11-03", “name”: “Sunoco”, “amount”: “30.12”, “category”: “None”}]”

    “category_options”: “[“Entertainment”, “Groceries”, “Other”, “Shopping”, “Financial”, “Food & Dining”, “Auto & Transport”, “Bills & Utilities”, “Home”, “Uncategorized”, “Income”]”

    “graph_options”: “[“Bar chart”, “Line chart”, “Pie chart”, “Histogram”, “Scatter Plot”]”

    }

    Example 2 Output:

    {

    “output_prompt”:

    “I'm sorry, I'm unable to answer that question. Please try again.”,

    

    “graph”: “”,

    “category_list”: “”,

    “answer_flag”: “False”

    }

    This question was unrelated to banking/personal finance so the chatbot will not answer the question.
    
    
    That is everything you should know to output the correct response. Here is the current input:"""

    user_input = f"""
    {{
    "user_promt": {json_string},
    "transactions": {plaid_dictionary},
    “category_options”: “[“Entertainment”, “Groceries”, “Other”, “Shopping”, “Financial”, “Food & Dining”, “Auto & Transport”, “Bills & Utilities”, “Home”, “Uncategorized”, “Income”]”
    “graph_options”: “[“Bar chart”, “Pie chart”, “Histogram”]”
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt + user_input
    )
  
    print(response.text)
    return response.text