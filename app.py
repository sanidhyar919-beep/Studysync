import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from supabase import create_client
from datetime import date, timedelta
import json
import re


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide"
)


# =========================
# AI CLIENT
# =========================

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)


# =========================
# SUPABASE CLIENT
# =========================

@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()


# =========================
# DATABASE FUNCTIONS
# =========================

def get_progress():
    result = (
        supabase
        .table("progress")
        .select(
            "study_progress, topics_completed, quizzes_completed"
        )
        .eq("id", 1)
        .single()
        .execute()
    )

    return result.data


def update_progress():
    current = get_progress()

    new_progress = min(
        100,
        current["study_progress"] + 5
    )

    new_topics = current["topics_completed"] + 1

    new_quizzes = current["quizzes_completed"] + 1

    (
        supabase
        .table("progress")
        .update({
            "study_progress": new_progress,
            "topics_completed": new_topics,
            "quizzes_completed": new_quizzes
        })
        .eq("id", 1)
        .execute()
    )


def save_quiz_result(
    topic,
    score,
    total,
    percentage
):

    (
        supabase
        .table("quiz_history")
        .insert({
            "topic": topic,
            "score": score,
            "total": total,
            "percentage": percentage,
            "date": str(date.today())
        })
        .execute()
    )


def save_study_activity():

    (
        supabase
        .table("study_activity")
        .upsert({
            "date": str(date.today())
        })
        .execute()
    )


def get_study_dates():

    result = (
        supabase
        .table("study_activity")
        .select("date")
        .execute()
    )

    return [
        row["date"]
        for row in result.data
    ]


def get_current_streak():

    dates = set(get_study_dates())

    today = date.today()

    streak = 0

    current_day = today

    while str(current_day) in dates:

        streak += 1

        current_day = (
            current_day -
            timedelta(days=1)
        )

    return streak


def get_quiz_history():

    result = (
        supabase
        .table("quiz_history")
        .select(
            "topic, score, total, percentage, date"
        )
        .order(
            "id",
            desc=True
        )
        .limit(10)
        .execute()
    )

    return result.data


# =========================
# AI FUNCTION
# =========================

def ask_ai(prompt):

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are StudySync, an AI study assistant. "
                    "Explain concepts in simple student-friendly language. "
                    "Use examples whenever useful."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5
    )

    return response.choices[0].message.content


# =========================
# SESSION STATE
# =========================

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []


# =========================
# SIDEBAR
# =========================

st.sidebar.title("📚 StudySync")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Study Material",
        "AI Study Assistant",
        "AI Notes Generator",
        "AI Quiz Generator",
        "Flashcards",
        "Progress Tracker"
    ]
)


# =========================
# HOME
# =========================

if page == "Home":

    st.title("📚 StudySync")

    st.subheader(
        "Your AI-Powered Study Companion"
    )

    progress = get_progress()

    streak = get_current_streak()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Study Progress",
            f'{progress["study_progress"]}%'
        )

    with col2:
        st.metric(
            "Topics Completed",
            progress["topics_completed"]
        )

    with col3:
        st.metric(
            "Quizzes Completed",
            progress["quizzes_completed"]
        )

    with col4:
        st.metric(
            "Current Streak",
            f"{streak} Days"
        )

    st.divider()

    st.markdown(
        """
        ### 🚀 What can StudySync do?

        - 📄 Upload and study PDF material
        - 🤖 Ask questions to AI
        - 📝 Generate AI notes
        - 🧠 Generate quizzes
        - 🃏 Create flashcards
        - 📊 Track your study progress
        """
    )


# =========================
# STUDY MATERIAL
# =========================

elif page == "Study Material":

    st.title("📄 Study Material")

    uploaded_file = st.file_uploader(
        "Upload your PDF",
        type=["pdf"]
    )

    if uploaded_file:

        reader = PdfReader(uploaded_file)

        text = ""

        for page_data in reader.pages:
            extracted = page_data.extract_text()

            if extracted:
                text += extracted + "\n"

        st.success(
            f"PDF loaded successfully! "
            f"{len(reader.pages)} pages found."
        )

        with st.expander("View extracted text"):

            st.write(
                text[:10000]
            )

        if st.button("Generate AI Notes"):

            with st.spinner(
                "Generating notes..."
            ):

                notes = ask_ai(
                    f"""
                    Create simple exam-oriented notes
                    from the following study material.

                    Use:
                    - headings
                    - bullet points
                    - important definitions
                    - examples

                    Material:

                    {text[:15000]}
                    """
                )

            st.markdown("## 📝 AI Notes")

            st.write(notes)


# =========================
# AI STUDY ASSISTANT
# =========================

elif page == "AI Study Assistant":

    st.title("🤖 AI Study Assistant")

    question = st.text_area(
        "Ask your study question"
    )

    if st.button("Ask AI"):

        if question.strip():

            with st.spinner(
                "Thinking..."
            ):

                answer = ask_ai(question)

            st.markdown("### Answer")

            st.write(answer)

            save_study_activity()

        else:

            st.warning(
                "Please enter a question."
            )


# =========================
# AI NOTES GENERATOR
# =========================

elif page == "AI Notes Generator":

    st.title("📝 AI Notes Generator")

    topic = st.text_input(
        "Enter topic"
    )

    if st.button("Generate Notes"):

        if topic.strip():

            with st.spinner(
                "Creating notes..."
            ):

                notes = ask_ai(
                    f"""
                    Create detailed but easy-to-understand
                    exam notes for:

                    {topic}

                    Include:
                    1. Definition
                    2. Important points
                    3. Working / explanation
                    4. Real-life example
                    5. Exam points
                    """
                )

            st.markdown("## 📚 Notes")

            st.write(notes)

            save_study_activity()

        else:

            st.warning(
                "Please enter a topic."
            )


# =========================
# AI QUIZ GENERATOR
# =========================

elif page == "AI Quiz Generator":

    st.title("🧠 AI Quiz Generator")

    topic = st.text_input(
        "Enter quiz topic",
        key="quiz_topic"
    )

    number = st.slider(
        "Number of questions",
        3,
        10,
        5
    )

    if st.button("Generate Quiz"):

        if not topic.strip():

            st.warning(
                "Please enter a topic."
            )

        else:

            with st.spinner(
                "Generating quiz..."
            ):

                prompt = f"""
                Create {number} multiple choice questions
                about {topic}.

                Return ONLY valid JSON.

                Format:

                [
                  {{
                    "question": "Question",
                    "options": [
                      "Option A",
                      "Option B",
                      "Option C",
                      "Option D"
                    ],
                    "answer": "Option A"
                  }}
                ]

                Make exactly {number} questions.
                """

                response = ask_ai(prompt)

                try:

                    cleaned = response.strip()

                    cleaned = re.sub(
                        r"```json",
                        "",
                        cleaned
                    )

                    cleaned = re.sub(
                        r"```",
                        "",
                        cleaned
                    )

                    start = cleaned.find("[")

                    end = cleaned.rfind("]") + 1

                    cleaned = cleaned[start:end]

                    questions = json.loads(
                        cleaned
                    )

                    st.session_state.quiz_questions = questions

                    st.session_state.quiz_score = None

                    st.session_state.quiz_submitted = False

                    st.success(
                        "Quiz generated successfully!"
                    )

                except Exception:

                    st.error(
                        "Quiz generation failed. "
                        "Please try again."
                    )


    # -------------------------
    # SHOW QUIZ
    # -------------------------

    questions = st.session_state.quiz_questions

    if questions:

        st.divider()

        st.subheader(
            "Answer the questions"
        )

        with st.form(
            "quiz_form"
        ):

            answers = []

            for i, q in enumerate(
                questions
            ):

                st.markdown(
                    f"### Q{i + 1}. {q['question']}"
                )

                selected = st.radio(
                    "Choose answer:",
                    q["options"],
                    key=f"q_{i}"
                )

                answers.append(
                    selected
                )

            submitted = st.form_submit_button(
                "Submit Quiz"
            )

        if submitted:

            score = 0

            for i, q in enumerate(
                questions
            ):

                if answers[i] == q["answer"]:
                    score += 1

            total = len(questions)

            percentage = round(
                (score / total) * 100
            )

            st.session_state.quiz_score = score

            st.session_state.quiz_submitted = True

            # Save to database
            save_quiz_result(
                topic,
                score,
                total,
                percentage
            )

            update_progress()

            save_study_activity()

            st.success(
                f"Quiz submitted! "
                f"Your score: {score}/{total}"
            )

            st.progress(
                percentage / 100
            )

            st.write(
                f"### Score: {percentage}%"
            )


        # -------------------------
        # ANSWER REVIEW
        # -------------------------

        if st.session_state.quiz_submitted:

            st.divider()

            st.subheader(
                "📋 Answer Review"
            )

            for i, q in enumerate(
                questions
            ):

                st.write(
                    f"**Q{i + 1}:** "
                    f"{q['question']}"
                )

                st.write(
                    f"Correct Answer: "
                    f"**{q['answer']}**"
                )


# =========================
# FLASHCARDS
# =========================

elif page == "Flashcards":

    st.title("🃏 AI Flashcards")

    topic = st.text_input(
        "Enter topic for flashcards"
    )

    number = st.slider(
        "Number of flashcards",
        3,
        15,
        5
    )

    if st.button(
        "Generate Flashcards"
    ):

        if not topic.strip():

            st.warning(
                "Please enter a topic."
            )

        else:

            with st.spinner(
                "Creating flashcards..."
            ):

                prompt = f"""
                Create {number} study flashcards
                about {topic}.

                Return ONLY valid JSON.

                Format:

                [
                  {{
                    "question": "Question",
                    "answer": "Answer"
                  }}
                ]

                Make exactly {number} cards.
                """

                response = ask_ai(prompt)

                try:

                    cleaned = response.strip()

                    cleaned = re.sub(
                        r"```json",
                        "",
                        cleaned
                    )

                    cleaned = re.sub(
                        r"```",
                        "",
                        cleaned
                    )

                    start = cleaned.find("[")

                    end = cleaned.rfind("]") + 1

                    cleaned = cleaned[start:end]

                    cards = json.loads(
                        cleaned
                    )

                    st.session_state.flashcards = cards

                    st.success(
                        "Flashcards generated!"
                    )

                    save_study_activity()

                except Exception:

                    st.error(
                        "Could not generate flashcards. "
                        "Please try again."
                    )


    if st.session_state.flashcards:

        st.divider()

        for i, card in enumerate(
            st.session_state.flashcards
        ):

            with st.expander(
                f"🃏 Card {i + 1}: "
                f"{card['question']}"
            ):

                st.write(
                    card["answer"]
                )


# =========================
# PROGRESS TRACKER
# =========================

elif page == "Progress Tracker":

    st.title("📊 Progress Tracker")

    progress = get_progress()

    streak = get_current_streak()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Study Progress",
            f'{progress["study_progress"]}%'
        )

    with col2:

        st.metric(
            "Topics Completed",
            progress["topics_completed"]
        )

    with col3:

        st.metric(
            "Quizzes Completed",
            progress["quizzes_completed"]
        )

    st.divider()

    st.subheader(
        "🔥 Current Streak"
    )

    st.metric(
        "Study Streak",
        f"{streak} Days"
    )

    st.divider()

    st.subheader(
        "📝 Recent Quiz History"
    )

    history = get_quiz_history()

    if history:

        for quiz in history:

            st.write(
                f"**{quiz['topic']}** — "
                f"{quiz['score']}/{quiz['total']} "
                f"({quiz['percentage']}%) — "
                f"{quiz['date']}"
            )

    else:

        st.info(
            "No quiz history yet."
        )
