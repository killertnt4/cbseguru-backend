import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Construct full path to chapter data
def get_chapter_path(grade, subject, chapter_num):
    base_path = os.path.join(os.path.dirname(__file__), "data")
    class_folder = f"class {grade}"
    chapter_filename = f"{chapter_num}.txt"
    full_path = os.path.join(base_path, class_folder, subject, chapter_filename)
    return full_path

# Load chapter text
def load_chapter_text(grade, subject, chapter_num):
    path = get_chapter_path(grade, subject, chapter_num)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.get_json()
        grade = str(data.get("grade", "")).strip()
        subject = data.get("subject", "").strip()
        chapter = str(data.get("chapter", "")).strip()
        question = data.get("question", "").strip()

        if not all([grade, subject, chapter, question]):
            return jsonify({"error": "Missing one or more required fields: grade, subject, chapter, question."}), 400

        chapter_text = load_chapter_text(grade, subject, chapter)
        if not chapter_text:
            return jsonify({"error": f"Chapter {chapter} not found for {subject} in Class {grade}."}), 404

        final_prompt = f"""
A student has said:

"{question}"

Below is content from Chapter {chapter} of Class {grade} {subject}:

{chapter_text}

If the message is a question or doubt, help them understand it clearly, step-by-step.
If it’s a casual message, respond naturally and guide them back to asking something from the chapter.
Avoid dumping too much info — be conversational, warm, and focused.
"""

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are a helpful and friendly CBSE teacher for Class {grade}, subject: {subject}.\n\n"
                        "You help students by answering their doubts and guiding them through the current chapter content.\n"
                        "- When students ask something specific, explain it clearly like a real teacher would.\n"
                        "- When they greet you or make casual conversation, respond warmly and encourage them to ask what they’re confused about.\n"
                        "- Don’t overwhelm them — keep things clear, light, and student-friendly.\n"
                        "- Always sound like you're chatting one-on-one with a real student. Be relaxed, encouraging, and human.\n"
                        "- Refer to the chapter content if needed, but use your own words and explanations.\n"
                        "- You can ask questions too, like a teacher would in a real conversation. Greet users warmly and ask them what they want to learn when they greet you. You don't have to overanalyze the prompt and consider everything to be a question."
                    )
                },
                {"role": "user", "content": final_prompt}
            ]
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "CBSE Teacher Bot"
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]

        return jsonify({"answer": reply})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
