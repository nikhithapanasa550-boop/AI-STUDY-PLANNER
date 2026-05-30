import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Study Planner", page_icon="📚", layout="wide")

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    """
<style>
.chat-bubble-user {
    background-color: #2563eb;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    width: fit-content;
    margin-left: auto;
    color: white;
}
.chat-bubble-ai {
    background-color: #1f2937;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    width: fit-content;
    color: white;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("⚙️ Controls")

study_goal = st.sidebar.text_input("🎯 Study Goal", "Crack exams")
hours = st.sidebar.slider("⏳ Study Hours per Day", 1, 12, 4)
days = st.sidebar.slider("📅 Number of Days", 1, 30, 7)

generate_btn = st.sidebar.button("🚀 Generate Plan")

# -----------------------------
# HEADER
# -----------------------------
st.title("📚 AI Study Planner")
st.caption("AI + Progress Tracker + PDF Export")

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "progress" not in st.session_state:
    st.session_state.progress = {}


# -----------------------------
# AI FUNCTION (SAFE)
# -----------------------------
def get_ai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful study planner AI."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception:
        return """
⚠️ AI unavailable (quota exceeded)

Basic Study Plan:
- Study 2–4 hours daily
- Break topics into small parts
- Revise every 2 days
- Practice questions regularly
- Track progress below

(Add billing to enable full AI)
"""


# -----------------------------
# PDF FUNCTION
# -----------------------------
def create_pdf(text):
    file_path = "study_plan.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    return file_path


# -----------------------------
# GENERATE PLAN
# -----------------------------
if generate_btn:
    prompt = f"""
    Create a structured study plan.

    Goal: {study_goal}
    Study hours: {hours}
    Days: {days}
    """

    ai_response = get_ai_response(prompt)

    # store for PDF
    st.session_state["last_plan"] = ai_response

    # initialize progress
    st.session_state.progress = {f"Day {i}": False for i in range(1, days + 1)}

    st.session_state.messages.append(
        {"role": "user", "content": f"Create plan for {study_goal}"}
    )

    st.session_state.messages.append({"role": "ai", "content": ai_response})

# -----------------------------
# 📊 PROGRESS TRACKER
# -----------------------------
st.subheader("📊 Progress Tracker")

if st.session_state.progress:
    completed = sum(st.session_state.progress.values())
    total = len(st.session_state.progress)
    percent = int((completed / total) * 100)

    st.progress(percent)
    st.write(f"{completed}/{total} days completed ({percent}%)")

    for day in st.session_state.progress:
        st.session_state.progress[day] = st.checkbox(
            day, value=st.session_state.progress[day]
        )
else:
    st.info("Generate a study plan to track progress")

# -----------------------------
# 📥 DOWNLOAD PDF
# -----------------------------
st.subheader("📥 Download Plan")

if "last_plan" in st.session_state:
    pdf_file = create_pdf(st.session_state["last_plan"])

    with open(pdf_file, "rb") as f:
        st.download_button("📄 Download Study Plan", f, file_name="study_plan.pdf")
else:
    st.info("Generate a plan first")

# -----------------------------
# 💬 CHAT
# -----------------------------
st.subheader("💬 Chat")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="chat-bubble-user">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="chat-bubble-ai">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )

# -----------------------------
# CHAT INPUT
# -----------------------------
user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    ai_reply = get_ai_response(user_input)

    st.session_state.messages.append({"role": "ai", "content": ai_reply})

    st.rerun()
