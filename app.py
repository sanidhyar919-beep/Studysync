import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from supabase import create_client
from datetime import date, timedelta
import json
import re


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS - NO HTML USED
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
        radial-gradient(
            circle at 10% 10%,
            rgba(88, 80, 255, 0.16),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(0, 190, 255, 0.10),
            transparent 30%
        ),
        #080b18;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background: #090d1c;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    h1 {
        font-weight: 800 !important;
        color: #ffffff !important;
    }

    h2, h3 {
        color: #ffffff !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 18px;
        padding: 20px;
        transition: 0.25s;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(100,120,255,0.45);
    }

    div[data-testid="stMetricLabel"] {
        color: #aeb8d4 !important;
    }

    div[data-testid="stMetricValue"] {
        color: white !important;
        font-weight: 800 !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        color: white;
        font-weight: 700;
        background: linear-gradient(
            90deg,
            #5967ff,
            #8b5cf6
        );
        transition: 0.25s;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow:
            0 10px 30px rgba(90,100,255,0.35);
    }

    .stTextInput input,
    .stTextArea textarea {
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.04);
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# GROQ
# =========================================================

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)


# =========================================================
# SUPABASE
# =========================================================

@st.cache_resource
def get_supabase():

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()


# =========================================================
# DATABASE
# =========================================================

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

    supabase.table("progress").update(
        {
            "study_progress": new_progress,
            "topics_completed":
                current["topics_completed"] + 1,
            "quizzes_completed":
                current["quizzes_completed"] + 1
        }
    ).eq("id", 1).execute()


def save_quiz_result(
    topic,
    score,
    total,
    percentage
):

    supabase.table("quiz_history").insert(
        {
            "topic": topic,
            "score": score,
            "total": total,
            "percentage": percentage,
            "date": str(date.today())
        }
    ).execute()


def save_study_activity():

    supabase.table("study_activity").upsert(
        {
            "date": str(date.today())
        }
    ).execute()


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

    current_day = date.today()

    streak = 0

    while str(current_day) in dates:

        streak += 1

        current_day -= timedelta(days=1)

    return streak


def get_quiz_history():

    result = (
        supabase
        .table("quiz_history")
        .select(
            "topic, score, total, percentage, date"
        )
        .order("id", desc=True)
        .limit(10)
        .execute()
    )

    return result.data


# =========================================================
# AI
# =========================================================

def ask_ai(prompt):

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content":
                """
                You are StudySync,
                an AI study assistant.

                Explain topics in simple,
                student-friendly language.

                Use headings, bullet points,
                examples and exam-oriented explanations.
                """
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5
    )

    return response.choices[0].message.content


# =========================================================
# SESSION STATE
# =========================================================

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📚 StudySync")

st.sidebar.caption(
    "AI Powered Study Companion"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📄 Study Material",
        "🤖 AI Study Assistant",
        "📝 AI Notes Generator",
        "🧠 AI Quiz Generator",
        "🃏 Flashcards",
        "📊 Progress Tracker"
    ]
)


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.title("Welcome to StudySync 🚀")

    st.subheader(
        "Your intelligent AI-powered study companion."
    )

    st.write(
        "Learn smarter. Practice better. "
        "Track your progress."
    )

    st.divider()

    progress = get_progress()

    streak = get_current_streak()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📈 Study Progress",
            f'{progress["study_progress"]}%'
        )

    with col2:

        st.metric(
            "📚 Topics Completed",
            progress["topics_completed"]
        )

    with col3:

        st.metric(
            "🧠 Quizzes Completed",
            progress["quizzes_completed"]
        )

    with col4:

        st.metric(
            "🔥 Current Streak",
            f"{streak} Days"
        )

    st.divider()

    st.subheader(
        "✨ Everything you need to study smarter"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            """
            📄 **Study Material**

            Upload PDFs and understand
            your study material with AI.
            """
        )

        st.info(
            """
            🤖 **AI Study Assistant**

            Ask questions and get
            simple explanations.
            """
        )

    with col2:

        st.info(
            """
            📝 **AI Notes**

            Generate structured,
            exam-oriented notes.
            """
        )

        st.info(
            """
            🧠 **AI Quiz**

            Test your knowledge
            with AI-generated quizzes.
            """
        )

    with col3:

        st.info(
            """
            🃏 **Flashcards**

            Create quick revision
            cards using AI.
            """
        )

        st.info(
            """
            📊 **Progress Tracker**

            Track your learning,
            quizzes and streak.
            """
        )


# =========================================================
# STUDY MATERIAL
# =========================================================

elif page == "📄 Study Material":

    st.title("📄 Study Material")

    st.write(
        "Upload your PDF and study it with AI."
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file:

        reader = PdfReader(uploaded_file)

        text = ""

        for pdf_page in reader.pages:

            extracted = pdf_page.extract_text()

            if extracted:
                text += extracted + "\n"

        st.success(
            f"PDF loaded successfully — "
            f"{len(reader.pages)} pages."
        )

        with st.expander("👀 View extracted text"):

            st.write(
                text[:10000]
            )

        if st.button("✨ Generate AI Notes"):

            with st.spinner(
                "AI is analyzing your PDF..."
            ):

                notes = ask_ai(
                    f"""
                    Create simple,
                    exam-oriented notes
                    from this material.

                    Include headings,
                    bullet points,
                    important definitions,
                    examples and key points.

                    Material:

                    {text[:15000]}
                    """
                )

            st.subheader("📝 AI Generated Notes")

            st.write(notes)

            save_study_activity()


# =========================================================
# AI ASSISTANT
# =========================================================

elif page == "🤖 AI Study Assistant":

    st.title("🤖 AI Study Assistant")

    st.write(
        "Ask anything related to your studies."
    )

    question = st.text_area(
        "💬 Your Question",
        placeholder=
        "Example: Explain pointers in C in simple language."
    )

    if st.button("🚀 Ask StudySync"):

        if question.strip():

            with st.spinner(
                "StudySync is thinking..."
            ):

                answer = ask_ai(question)

            st.subheader("💡 Answer")

            st.write(answer)

            save_study_activity()

        else:

            st.warning(
                "Please enter a question."
            )


# =========================================================
# NOTES
# =========================================================

elif page == "📝 AI Notes Generator":

    st.title("📝 AI Notes Generator")

    st.write(
        "Generate easy and exam-ready notes."
    )

    topic = st.text_input(
        "📚 Enter Topic",
        placeholder="Example: Operating System"
    )

    if st.button("✨ Generate Notes"):

        if topic.strip():

            with st.spinner(
                "Creating your notes..."
            ):

                notes = ask_ai(
                    f"""
                    Create detailed but easy
                    exam-oriented notes for:

                    {topic}

                    Include:

                    1. Definition
                    2. Important points
                    3. Working
                    4. Real-life example
                    5. Advantages
                    6. Disadvantages
                    7. Important exam points
                    """
                )

            st.subheader("📚 Your Notes")

            st.write(notes)

            save_study_activity()

        else:

            st.warning(
                "Please enter a topic."
            )


# =========================================================
# QUIZ
# =========================================================

elif page == "🧠 AI Quiz Generator":

    st.title("🧠 AI Quiz Generator")

    st.write(
        "Generate a quiz and test your knowledge."
    )

    topic = st.text_input(
        "📚 Quiz Topic",
        placeholder="Example: C Programming"
    )

    number = st.slider(
        "Number of Questions",
        3,
        10,
        5
    )

    if st.button("🎯 Generate Quiz"):

        if not topic.strip():

            st.warning(
                "Please enter a topic."
            )

        else:

            with st.spinner(
                "Generating quiz..."
            ):

                prompt = f"""
                Create {number} multiple choice
                questions about {topic}.

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

                questions = json.loads(cleaned)

                st.session_state.quiz_questions = questions

                st.session_state.quiz_submitted = False

                st.session_state.quiz_score = None

                st.success(
                    "🎉 Quiz generated!"
                )

            except Exception:

                st.error(
                    "Quiz generation failed. "
                    "Please try again."
                )

    questions = st.session_state.quiz_questions

    if questions:

        st.divider()

        st.subheader(
            "📝 Answer the Questions"
        )

        with st.form("quiz_form"):

            answers = []

            for i, question in enumerate(questions):

                st.markdown(
                    f"### Q{i + 1}. "
                    f"{question['question']}"
                )

                selected = st.radio(
                    "Select answer:",
                    question["options"],
                    key=f"question_{i}"
                )

                answers.append(selected)

            submitted = st.form_submit_button(
                "✅ Submit Quiz"
            )

        if submitted:

            score = 0

            for i, question in enumerate(questions):

                if answers[i] == question["answer"]:

                    score += 1

            total = len(questions)

            percentage = round(
                score / total * 100
            )

            st.session_state.quiz_score = score

            st.session_state.quiz_submitted = True

            save_quiz_result(
                topic,
                score,
                total,
                percentage
            )

            update_progress()

            save_study_activity()

            st.success(
                f"🎉 Your score: {score}/{total}"
            )

            st.progress(
                percentage / 100
            )

            st.subheader(
                f"🏆 Score: {percentage}%"
            )

        if st.session_state.quiz_submitted:

            st.divider()

            st.subheader(
                "📋 Answer Review"
            )

            for i, question in enumerate(questions):

                st.write(
                    f"**Q{i + 1}.** "
                    f"{question['question']}"
                )

                st.success(
                    f"Correct Answer: "
                    f"{question['answer']}"
                )


# =========================================================
# FLASHCARDS
# =========================================================

elif page == "🃏 Flashcards":

    st.title("🃏 AI Flashcards")

    st.write(
        "Create quick revision cards using AI."
    )

    topic = st.text_input(
        "📚 Flashcard Topic",
        placeholder="Example: Data Structures"
    )

    number = st.slider(
        "Number of Flashcards",
        3,
        15,
        5
    )

    if st.button("✨ Generate Flashcards"):

        if not topic.strip():

            st.warning(
                "Please enter a topic."
            )

        else:

            with st.spinner(
                "Creating flashcards..."
            ):

                prompt = f"""
                Create {number} flashcards
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

                cards = json.loads(cleaned)

                st.session_state.flashcards = cards

                save_study_activity()

                st.success(
                    "🎉 Flashcards generated!"
                )

            except Exception:

                st.error(
                    "Flashcards could not be generated."
                )

    if st.session_state.flashcards:

        st.divider()

        st.subheader(
            "🧠 Your Flashcards"
        )

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


# =========================================================
# PROGRESS
# =========================================================

elif page == "📊 Progress Tracker":

    st.title("📊 Progress Tracker")

    st.write(
        "Track your StudySync learning journey."
    )

    progress = get_progress()

    streak = get_current_streak()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📈 Study Progress",
            f'{progress["study_progress"]}%'
        )

    with col2:

        st.metric(
            "📚 Topics Completed",
            progress["topics_completed"]
        )

    with col3:

        st.metric(
            "🧠 Quizzes Completed",
            progress["quizzes_completed"]
        )

    st.divider()

    st.subheader("🔥 Current Streak")

    st.metric(
        "Study Streak",
        f"{streak} Days"
    )

    st.progress(
        min(streak / 30, 1.0)
    )

    st.divider()

    st.subheader(
        "📝 Recent Quiz History"
    )

    history = get_quiz_history()

    if history:

        for quiz in history:

            st.info(
                f"""
                🧠 **{quiz["topic"]}**

                Score: {quiz["score"]}/{quiz["total"]}

                Percentage: {quiz["percentage"]}%

                Date: {quiz["date"]}
                """
            )

    else:

        st.info(
            "No quiz history yet."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📚 StudySync • Learn Smarter • Practice Better • Track Progress"
)
