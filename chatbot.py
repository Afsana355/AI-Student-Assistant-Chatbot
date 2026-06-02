import json
import random
import re
import tkinter as tk
from tkinter import scrolledtext
import nltk
from nltk.tokenize import word_tokenize

# Download required tokenizer data
nltk.download('punkt')
nltk.download('punkt_tab')

# Load intents
with open('intents.json') as file:
    data = json.load(file)

# Safe tokenizer wrapper to ensure required resources are downloaded
def safe_word_tokenize(text):
    try:
        return word_tokenize(text)
    except LookupError:
        nltk.download('punkt_tab')
        return word_tokenize(text)

# Normalize text for better matching
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

STOPWORDS = {
    'a', 'an', 'the', 'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being',
    'i', 'you', 'your', 'yours', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours',
    'it', 'its', 'this', 'that', 'these', 'those', 'what', 'who', 'where',
    'when', 'why', 'how', 'can', 'could', 'would', 'should', 'do', 'does',
    'did', 'have', 'has', 'had', 'will', 'shall', 'may', 'might', 'must',
    'and', 'or', 'but', 'with', 'for', 'to', 'in', 'on', 'at', 'by', 'from',
    'about', 'of', 'as', 'just', 'really', 'so', 'if', 'then', 'also', 'too'
}

def content_words(words):
    return [word for word in words if word not in STOPWORDS]

# Function to get chatbot response
def chatbot_response(user_input):
    user_text = normalize_text(user_input)
    user_words = safe_word_tokenize(user_text)
    user_content = content_words(user_words)

    best_score = 0
    best_response = None

    for intent in data['intents']:
        for pattern in intent['patterns']:
            pattern_text = normalize_text(pattern)
            pattern_words = safe_word_tokenize(pattern_text)
            pattern_content = content_words(pattern_words)

            if pattern_text == user_text or pattern_text in user_text:
                return random.choice(intent['responses'])

            if pattern_content and user_content:
                overlap = sum(1 for word in pattern_content if word in user_content)
                score = overlap / len(pattern_content)
            else:
                overlap = sum(1 for word in pattern_words if word in user_words)
                score = overlap / len(pattern_words)

            if score > best_score:
                best_score = score
                best_response = random.choice(intent['responses'])

    if best_score >= 0.6:
        return best_response

    return "Sorry, I do not understand your question."

# Send message function
def send_message():

    user_message = entry_box.get()

    if user_message.strip() == "":
        return

    chat_area.insert(tk.END, "You: " + user_message + "\n")

    response = chatbot_response(user_message)

    chat_area.insert(tk.END, "Bot: " + response + "\n\n")

    entry_box.delete(0, tk.END)

if __name__ == "__main__":
    # GUI Window
    window = tk.Tk()
    window.title("AI Student Assistant Chatbot")
    window.geometry("600x500")
    window.configure(bg="#f0f0f0")

    # Title
    title_label = tk.Label(
        window,
        text="AI Student Assistant Chatbot",
        font=("Arial", 18, "bold"),
        bg="#f0f0f0"
    )

    title_label.pack(pady=10)

    # Chat Area
    chat_area = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        width=70,
        height=20,
        font=("Arial", 11)
    )

    chat_area.pack(padx=10, pady=10)

    # Entry Box
    entry_box = tk.Entry(window, width=50, font=("Arial", 12))
    entry_box.pack(side=tk.LEFT, padx=10, pady=10)

    # Send Button
    send_button = tk.Button(
        window,
        text="Send",
        width=12,
        font=("Arial", 11, "bold"),
        command=send_message
    )

    send_button.pack(side=tk.LEFT, padx=5)

    # Run GUI
    window.mainloop()
