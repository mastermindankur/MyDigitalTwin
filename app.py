# Load environment variables from a .env file
from dotenv import load_dotenv
from openai import OpenAI
import os
import requests
import gradio as gr
import json

# For HTML parsing and crawling
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib

# Function to crawl and read visible text from a website recursively
def read_profile_from_web(url, max_depth=3, visited=None, seen_hashes=None, found_urls=None):
    if visited is None:
        visited = set()
    if seen_hashes is None:
        seen_hashes = set()
    if found_urls is None:
        found_urls = set()

    url = url.rstrip('/')  # Normalize URL

    if url in visited or max_depth < 0:
        return "", found_urls

    visited.add(url)
    print(f"Visiting: {url}")

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"Failed to fetch {url} — Status code: {response.status_code}")
            return "", found_urls

        # Skip non-HTML content
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            print(f"Non-HTML content at {url}, skipping.")
            return "", found_urls

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract visible text
        text_content = ' '.join(soup.stripped_strings).strip()

        # Detect and skip duplicate content
        content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
        if content_hash in seen_hashes:
            print(f"Duplicate content found, skipping {url}")
            return "", found_urls
        seen_hashes.add(content_hash)

        # Recursively crawl internal links
        base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
        sub_content = ""

        for link in soup.find_all('a', href=True):
            href = link['href']
            parsed_href = urlparse(href)

            if parsed_href.fragment:
                continue  # Skip page fragment links like "#about"

            full_url = urljoin(base_url, href).rstrip('/')
            if full_url.startswith("data:"):
                continue  # Skip data URLs

            found_urls.add(full_url)

            if urlparse(full_url).netloc == urlparse(url).netloc:
                # Recursively read sub-page content
                new_text, _ = read_profile_from_web(full_url, max_depth=max_depth - 1,
                                                    visited=visited, seen_hashes=seen_hashes,
                                                    found_urls=found_urls)
                sub_content += "\n" + new_text

        print(f"found_urls: {found_urls}")
        return text_content + "\n" + sub_content, found_urls

    except Exception as e:
        print(f"Error reading from web: {e}")
        return "", found_urls

# Load environment variables
load_dotenv(override=True)

# Instantiate OpenAI client using GEMINI-compatible endpoint
gemini = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"), 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Load Pushover credentials
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"
NAME = os.getenv("NAME")

# Utility to send Pushover push notifications
def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)


import os
import requests
bot_token=os.getenv("BOT_TOKEN")
chat_id=os.getenv("CHAT_ID")

def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Sends a message to a Telegram user or group via a bot.

    Args:
        bot_token (str): Telegram bot token from BotFather.
        chat_id (str): The chat ID to which the message will be sent.
        message (str): The message text to send.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    print(bot_token)
    print(chat_id)
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

# Sample push to verify Pushover setup
push("hello ankur khera and aishwarya gupta!")
send_telegram_message(bot_token,chat_id,"hello ankur khera and aishwarya gupta!")

# Function to record user contact details
def record_user_details(email, name="Name not provided", notes="not provided"):
    send_telegram_message(bot_token,chat_id,f"Tool Called: Recording interest from Name: {name} with Email: {email} and notes {notes}")
    #push(f"Tool Called: Recording interest from Name: {name} with Email: {email} and notes {notes}")
    return {"recorded": "ok"}

# Function to record unanswered questions
def record_unknown_question(question):
    send_telegram_message(bot_token,chat_id,f"Tool Called: Recording Question: {question}, which i could not answer")
    #push(f"Tool Called: Recording Question: {question}, which i could not answer")
    return {"recorded": "ok"}

# Function to record all questions
def record_all_question(question, user_message):
    send_telegram_message(bot_token,chat_id,f"Tool Called: New message received - Question/Message: {user_message}")
    #push(f"Tool Called: New message received - Question/Message: {user_message}")
    return {"recorded": "ok"}

# Tool JSON schema for recording user details
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Any additional context from the conversation"}
        },
        "required": ["email", "name"],
        "additionalProperties": False
    },
    "strict": True
}

# Tool JSON schema for recording unknown questions
record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False
    },
    "strict": True
}

# Tool JSON schema for recording all questions
record_all_question_json = {
    "name": "record_all_question",
    "description": "Use this tool to record every message/question received from users",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "Whether this is a question or not"},
            "user_message": {"type": "string", "description": "The actual message from the user"}
        },
        "required": ["question", "user_message"],
        "additionalProperties": False
    },
    "strict": True
}

# Register tools
tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": record_all_question_json}
]

# Function to process tool calls dynamically
def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)

        # Call the appropriate function
        if tool_name == "record_user_details":
            message = f"Tool Called: User Contact - Name: {arguments.get('name', 'Not provided')}, Email: {arguments.get('email')}"
            result = record_user_details(**arguments)
        elif tool_name == "record_unknown_question":
            message = f"Tool Called: Unknown Question: {arguments.get('question')}"
            result = record_unknown_question(**arguments)
        elif tool_name == "record_all_question":
            message = f"Tool Called: Received Message: {arguments.get('user_message')}"
            result = record_all_question(**arguments)

        results.append({
            "role": "tool",
            "content": json.dumps(result),
            "tool_call_id": tool_call.id
        })
    return results

# Virtual Assistant class definition
class Me:
    def __init__(self):
        self.name = os.getenv("NAME")
        
        # Crawl and read personal website
        self.user_content = read_profile_from_web(os.getenv("HOME_PAGE_URL"))

        # System prompt to guide LLM behavior
        self.system_prompt = f"""You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background which you can use to answer questions. \
Be professional and engaging and respectful with a mild humour, as if talking to a friend, potential client or future employer who came across the website. \
You have access to 3 tools that you should use appropriately: \
1) record_user_details - use this when a user is interested in being in touch and provides an email address \
2) record_unknown_question - use this when you encounter a question you couldn't answer \
3) record_all_question - use this for EVERY message received to ensure it's logged. This is important for tracking all interactions."""

        self.system_prompt += f"\n\n## Content scraped from {self.name}'s website:\n{self.user_content}\n\n"
        self.system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."

    # Chat method to handle LLM responses and tool calls
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt}] + history + [{"role": "user", "content": message}]
        done = False

        #push(f"Message recieved from user: {message}")
        send_telegram_message(bot_token,chat_id,f"Message recieved from user: {message}")

        while not done:
            # Make LLM call (Gemini-style response parsing)
            response = gemini.beta.chat.completions.parse(
                model="gemini-2.0-flash", messages=messages, tools=tools
            )
            
            finish_reason = response.choices[0].finish_reason
            print(finish_reason)
            
            # If tool use is requested
            if finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = handle_tool_calls(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True

        push(f"Response from LLM: {response.choices[0].message.content}")
        send_telegram_message(bot_token,chat_id,f"Response from LLM: {response.choices[0].message.content}")
        return response.choices[0].message.content

# Launch the Gradio chatbot UI
if __name__ == "__main__":
    me = Me()

    gr.ChatInterface(
        fn=me.chat,
        type="messages",
        title=f"Welcome to {NAME}'s Digital Twin",
        examples=[
            "What is your experience?",
            "What are your recent projects?",
            "How can I contact you?"
        ],
        chatbot=gr.Chatbot(
            value=[
                {"role": "assistant", "content": f"Hi there! 👋 I'm {NAME}'s virtual assistant. Ask me anything about my career or background."}
            ],
            type="messages",
            height="70vh"
        )
    ).launch()
