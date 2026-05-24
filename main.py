import os
import json
from flask import Flask, request, jsonify, render_template
from google import genai 
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_KEY")

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
CHAT_NAME = "Drama Bean"

#open json file
with open("data/dramas.json", 'r') as f:
    dramas = json.load(f)

def build_drama_context():
    context = ""
    for drama in dramas:
        context += f"""
Title: {drama['title']}
Year: {drama['year']}
Genre: {', '.join(drama['genre'])}
Mood: {', '.join(drama['mood'])}
Synopsis: {drama['synopsis']}
Cast: {', '.join(drama['cast'])}
Rating: {drama['rating']}
Where to watch: {', '.join(drama['where_to_watch'])}
---"""
    return context

SYSTEM_PROMPT = f"""You are {CHAT_NAME}, a friendly and passionate Chinese drama (cdrama) expert chatbot.
You help users discover, learn about, and get recommendations for Chinese dramas.
 
You can help with:
- Recommending dramas based on mood, genre, or what they've enjoyed before
- Sharing drama summaries and plot details
- Giving reviews from other users
- Providing cast and actor information
- Telling users where they can watch dramas
- Giving dates of when dramas were released
 
Always be enthusiastic and warm. If someone seems new to cdramas, be welcoming and suggest beginner-friendly picks.
If a user asks about a drama not in your database, use your general knowledge to help them.
 
Here is your drama database:
{build_drama_context()}
 
When recommending dramas, explain WHY you think they'd enjoy it based on what they told you.
Keep responses conversational and friendly, not like a boring list.
"""
coversation_history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods = ["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    coversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    full_conversation = SYSTEM_PROMPT + "\n\n"
    for msg in coversation_history:
        full_conversation += f"{msg["role"]}: {msg['content']}\n"
        
    response = client.models.generate_content(
        model = "gemini-2.0-flash",
        contents=full_conversation
    )
    
    bot_reply = response.text

    coversation_history.append({
        "role": "chat_bot",
        "content": user_message
    })

    return jsonify({"replay": bot_reply})

if __name__ == "__main__":
    app.run(debug = True)