import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from supabase import create_client
from datetime import date, timedelta
import json
import re


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# MODERN UI / CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* =========================
   MAIN BACKGROUND
========================= */

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(91, 74, 255, 0.18),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(0, 200, 255, 0.12),
            transparent 30%
        ),
        radial-gradient(
            circle at 50% 90%,
            rgba(139, 92, 246, 0.10),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #080b18 0%,
            #0d1024 45%,
            #080b18 100%
        );

    color: #f5f7ff;
}


/* =========================
   PAGE ANIMATION
========================= */

.main .block-container {
    animation: pageFade 0.7s ease-in-out;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

@keyframes pageFade {

    from {
        opacity: 0;
        transform: translateY(15px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }

}


/* =========================
   HEADINGS
========================= */

h1 {
    font-size: 2.7rem !important;
    font-weight: 800 !important;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #8ea2ff,
            #55d6ff
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

h2,
h3 {
    color: #f5f7ff !important;
}


/* =========================
   SIDEBAR
========================= */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            rgba(13, 16, 36, 0.98),
            rgba(8, 11, 24, 0.98)
        );

    border-right:
        1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] h1 {

    font-size: 1.8rem !important;

}


/* =========================
   METRIC CARDS
========================= */

div[data-testid="stMetric"] {

    background:
        rgba(255,255,255,0.055);

    border:
        1px solid rgba(255,255,255,0.09);

    border-radius:
        18px;

    padding:
        20px;

    backdrop-filter:
        blur(14px);

    transition:
        all 0.3s ease;

    box-shadow:
        0 8px 30px rgba(0,0,0,0.20);
}

div[data-testid="stMetric"]:hover {

    transform:
        translateY(-6px);

    border-color:
        rgba(120,140,255,0.45);

    box-shadow:
        0 15px 40px rgba(80,90,255,0.20);
}

div[data-testid="stMetricLabel"] {

    color:
        #aeb8d4 !important;
}

div[data-testid="stMetricValue"] {

    color:
        #ffffff !important;

    font-weight:
        800 !important;
}


/* =========================
   BUTTONS
========================= */

.stButton > button {

    width:
        100%;

    border:
        none;

    border-radius:
        12px;

    padding:
        0.7rem 1.2rem;

    font-weight:
        700;

    color:
        white;

    background:
        linear-gradient(
            90deg,
            #5967ff,
            #8b5cf6
        );

    transition:
        all 0.25s ease;

    box-shadow:
        0 6px 20px rgba(91,103,255,0.25);
}

.stButton > button:hover {

    transform:
        translateY(-3px) scale(1.01);

    box-shadow:
        0 12px 30px rgba(91,103,255,0.40);
}

.stButton > button:active {

    transform:
        scale(0.97);
}


/* =========================
   INPUTS
========================= */

.stTextInput input,
.stTextArea textarea {

    background:
        rgba(255,255,255,0.055) !important;

    color:
        white !important;

    border:
        1px solid rgba(255,255,255,0.10) !important;

    border-radius:
        12px !important;
}


/* =========================
   SELECT BOX
========================= */

div[data-baseweb="select"] > div {

    background:
        rgba(255,255,255,0.055) !important;

    color:
        white !important;

    border:
        1px solid rgba(255,255,255,0.10) !important;

    border-radius:
        12px !important;
}


/* =========================
   FILE UPLOADER
========================= */

section[data-testid="stFileUploader"] {

    background:
        rgba(255,255,255,0.04);

    border:
        1px dashed rgba(120,140,255,0.45);

    border-radius:
        16px;

    padding:
        10px;

    transition:
        0.3s ease;
}

section[data-testid="stFileUploader"]:hover {

    border-color:
        #7c8cff;

    background:
        rgba(100,110,255,0.07);
}


/* =========================
   EXPANDERS
========================= */

div[data-testid="stExpander"] {

    background:
        rgba(255,255,255,0.045);

    border:
        1px solid rgba(255,255,255,0.08);

    border-radius:
        14px;

    transition:
        0.3s ease;
}

div[data-testid="stExpander"]:hover {

    border-color:
        rgba(120,140,255,0.35);
}


/* =========================
   PROGRESS BAR
========================= */

div[data-testid="stProgressBar"] > div > div {

    background:
        linear-gradient(
            90deg,
            #5967ff,
            #8b5cf6,
            #55d6ff
        );

    background-size:
        200% 100%;

    animation:
        progressGlow 2s linear infinite;
}

@keyframes progressGlow {

    0% {
        background-position:
            0% 50%;
    }

    100% {
        background-position:
            200% 50%;
    }

}


/* =========================
   ALERTS
========================= */

div[data-testid="stAlert"] {

    border-radius:
        14px;

    backdrop-filter:
        blur(10px);
}


/* =========================
   DIVIDER
========================= */

hr {

    border-color:
        rgba(255,255,255,0.08) !important;
}


/* =========================
   RADIO BUTTONS
========================= */

div[role="radiogroup"] label {

    background:
        rgba(255,255,255,0.035);

    border-radius:
        10px;

    padding:
        8px 12px;

    margin-bottom:
        5px;

    transition:
        0.2s ease;
}

div[role="radiogroup"] label:hover {

    background:
        rgba(100,110,255,0.12);
}


/* =========================
   HOME FEATURE CARDS
========================= */

.feature-card {

    background:
        rgba(255,255,255,0.045);

    border:
        1px solid rgba(255,255,255,0.08);

    border-radius:
        18px;

    padding:
        22px;

    margin-bottom:
        15px;

    transition:
        all 0.3s ease;

    backdrop-filter:
        blur(12px);
}

.feature-card:hover {

    transform:
        translateY(-5px);

    border-color:
        rgba(120,140,255,0.35);

    box-shadow:
        0 15px 35px rgba(70,80,255,0.15);
}

.feature-icon {

    font-size:
        2rem;
}

.feature-title {

    font-size:
        1.1rem;

    font-weight:
        700;

    margin-top:
        8px;
}

.feature-text {

    color:
        #aeb8d4;

    font-size:
        0.9rem;

    margin-top:
        5px;
}


/* =========================
   HERO SECTION
========================= */

.hero {

    padding:
        35px;

    border-radius:
        24px;

    margin-bottom:
        30px;

    background:
        linear-gradient(
            135deg,
            rgba(89,103,255,0.16),
            rgba(139,92,246,0.10),
            rgba(0,200,255,0.07)
        );

    border:
        1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 20px 60px rgba(0,0,0,0.25);

    animation:
        heroFloat 4s ease-in-out infinite;
}

@keyframes heroFloat {

    0%,
    100% {
        transform:
            translateY(0);
    }

    50% {
        transform:
            translateY(-5px);
    }

}

.hero-title {

    font-size:
        3.2rem;

    font-weight:
        800;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #8ea2ff,
            #55d6ff
        );

    -webkit-background-clip:
        text;

    -webkit-text-fill-color:
        transparent;
}

.hero-subtitle {

    color:
        #aeb8d4;

    font-size:
        1.1rem;

    margin-top:
        8px;
}


/* =========================
   SCROLLBAR
========================= */

::-webkit-scrollbar {

    width:
        8px;
}

::-webkit-scrollbar-track {

    background:
        #080b18;
}

::-webkit-scrollbar-thumb {

    background:
        linear-gradient(
            #5967ff,
            #8b5cf6
        );

    border-radius:
        10px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# AI CLIENT
# =========================================================

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)


# =========================================================
# SUPABASE CLIENT
# =========================================================

@st.cache_resource
def get_supabase():

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()


# =========================================================
# DATABASE FUNCTIONS
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

    new_topics = (
        current["topics_completed"] + 1
    )

    new_quizzes = (
        current["quizzes_completed"] + 1
    )

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

    dates = set(
        get_study_dates()
    )

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


# =========================================================
# AI FUNCTION
# =========================================================

def ask_ai(prompt):

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": """
You are StudySync, an AI study assistant.

Explain concepts in simple student-friendly language.

Use:
- clear headings
- bullet points
- examples
- exam-oriented explanations

Avoid unnecessarily complicated language.
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


if "quiz_score" not in st.session_state:

    st.session_state.quiz_score = None


if "quiz_submitted" not in st.session_state:

    st.session_state.quiz_submitted = False


if "flashcards" not in st.session_state:

    st.session_state.flashcards = []


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    """
    <div style="
        text-align:center;
        padding:15px 5px 20px 5px;
    ">

        <div style="
            font-size:3rem;
            animation: float 3s ease-in-out infinite;
        ">
            📚
        </div>

        <div style="
            font-size:1.7rem;
            font-weight:800;
            color:white;
        ">
            StudySync
        </div>

        <div style="
            color:#8995b5;
            font-size:0.8rem;
            margin-top:4px;
        ">
            AI Powered Study Companion
        </div>

    </div>

    <style>

    @keyframes float {

        0%, 100% {
            transform:translateY(0);
        }

        50% {
            transform:translateY(-6px);
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


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


# =========================================================
# HOME
# =========================================================

if page == "Home":

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                Welcome to StudySync 🚀
            </div>

            <div class="hero-subtitle">
                Your intelligent AI-powered study companion.
                Learn smarter. Practice better. Track your progress.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


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

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    📄
                </div>

                <div class="feature-title">
                    Study Material
                </div>

                <div class="feature-text">
                    Upload PDFs and turn your
                    study material into easy notes.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🤖
                </div>

                <div class="feature-title">
                    AI Study Assistant
                </div>

                <div class="feature-text">
                    Ask questions and get
                    simple AI-powered explanations.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    📝
                </div>

                <div class="feature-title">
                    AI Notes
                </div>

                <div class="feature-text">
                    Generate structured,
                    exam-oriented notes instantly.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🧠
                </div>

                <div class="feature-title">
                    AI Quiz
                </div>

                <div class="feature-text">
                    Test your knowledge with
                    automatically generated quizzes.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🃏
                </div>

                <div class="feature-title">
                    Flashcards
                </div>

                <div class="feature-text">
                    Create quick revision cards
                    using AI.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    📊
                </div>

                <div class="feature-title">
                    Progress Tracker
                </div>

                <div class="feature-text">
                    Track quizzes, topics,
                    streaks and study progress.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# STUDY MATERIAL
# =========================================================

elif page == "Study Material":

    st.title("📄 Study Material")

    st.write(
        "Upload your PDF and let StudySync help you understand it."
    )


    uploaded_file = st.file_uploader(
        "Upload your PDF",
        type=["pdf"]
    )


    if uploaded_file:

        reader = PdfReader(
            uploaded_file
        )

        text = ""


        for page_data in reader.pages:

            extracted = page_data.extract_text()

            if extracted:

                text += extracted + "\n"


        st.success(
            f"PDF loaded successfully! "
            f"{len(reader.pages)} pages found."
        )


        with st.expander(
            "👀 View extracted text"
        ):

            st.write(
                text[:10000]
            )


        if st.button(
            "✨ Generate AI Notes"
        ):

            with st.spinner(
                "AI is analyzing your material..."
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
- important exam points

Material:

{text[:15000]}
"""
                )


            st.markdown(
                "## 📝 AI Generated Notes"
            )

            st.write(
                notes
            )

            save_study_activity()


# =========================================================
# AI STUDY ASSISTANT
# =========================================================

elif page == "AI Study Assistant":

    st.title(
        "🤖 AI Study Assistant"
    )

    st.write(
        "Ask anything related to your studies."
    )


    question = st.text_area(
        "💬 What do you want to know?",
        placeholder="Example: Explain pointers in C in simple language..."
    )


    if st.button(
        "🚀 Ask StudySync"
    ):

        if question.strip():

            with st.spinner(
                "StudySync is thinking..."
            ):

                answer = ask_ai(
                    question
                )


            st.markdown(
                "### 💡 Answer"
            )

            st.write(
                answer
            )

            save_study_activity()


        else:

            st.warning(
                "Please enter a question."
            )


# =========================================================
# AI NOTES GENERATOR
# =========================================================

elif page == "AI Notes Generator":

    st.title(
        "📝 AI Notes Generator"
    )

    st.write(
        "Generate easy-to-understand, exam-ready notes."
    )


    topic = st.text_input(
        "📚 Enter your topic",
        placeholder="Example: Operating System"
    )


    if st.button(
        "✨ Generate Notes"
    ):

        if topic.strip():

            with st.spinner(
                "Creating your notes..."
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
5. Advantages
6. Disadvantages
7. Important exam points
"""
                )


            st.markdown(
                "## 📚 Your AI Notes"
            )

            st.write(
                notes
            )

            save_study_activity()


        else:

            st.warning(
                "Please enter a topic."
            )


# =========================================================
# AI QUIZ GENERATOR
# =========================================================

elif page == "AI Quiz Generator":

    st.title(
        "🧠 AI Quiz Generator"
    )

    st.write(
        "Generate an interactive quiz and test your knowledge."
    )


    topic = st.text_input(
        "📚 Quiz Topic",
        key="quiz_topic",
        placeholder="Example: C Programming"
    )


    number = st.slider(
        "Number of Questions",
        3,
        10,
        5
    )


    if st.button(
        "🎯 Generate Quiz"
    ):

        if not topic.strip():

            st.warning(
                "Please enter a topic."
            )

        else:

            with st.spinner(
                "Generating your quiz..."
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

Every question must have exactly
four options and one correct answer.
"""


                response = ask_ai(
                    prompt
                )


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

                    end = (
                        cleaned.rfind("]") + 1
                    )


                    cleaned = cleaned[
                        start:end
                    ]


                    questions = json.loads(
                        cleaned
                    )


                    st.session_state.quiz_questions = questions

                    st.session_state.quiz_score = None

                    st.session_state.quiz_submitted = False


                    st.success(
                        "🎉 Quiz generated successfully!"
                    )


                except Exception:

                    st.error(
                        "Quiz generation failed. Please try again."
                    )


    questions = (
        st.session_state.quiz_questions
    )


    if questions:

        st.divider()

        st.subheader(
            "📝 Answer the Questions"
        )


        with st.form(
            "quiz_form"
        ):

            answers = []


            for i, q in enumerate(
                questions
            ):

                st.markdown(
                    f"""
                    ### Q{i + 1}. {q["question"]}
                    """
                )


                selected = st.radio(
                    "Choose your answer:",
                    q["options"],
                    key=f"q_{i}"
                )


                answers.append(
                    selected
                )


            submitted = st.form_submit_button(
                "✅ Submit Quiz"
            )


        if submitted:

            score = 0


            for i, q in enumerate(
                questions
            ):

                if (
                    answers[i]
                    ==
                    q["answer"]
                ):

                    score += 1


            total = len(
                questions
            )


            percentage = round(
                (score / total) * 100
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
                f"🎉 Quiz submitted! "
                f"Score: {score}/{total}"
            )


            st.progress(
                percentage / 100
            )


            st.markdown(
                f"## 🏆 Score: {percentage}%"
            )


        if (
            st.session_state.quiz_submitted
        ):

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

                st.success(
                    f"Correct Answer: "
                    f"{q['answer']}"
                )


# =========================================================
# FLASHCARDS
# =========================================================

elif page == "Flashcards":

    st.title(
        "🃏 AI Flashcards"
    )

    st.write(
        "Generate quick revision cards for any topic."
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


    if st.button(
        "✨ Generate Flashcards"
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


                response = ask_ai(
                    prompt
                )


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

                    end = (
                        cleaned.rfind("]") + 1
                    )


                    cleaned = cleaned[
                        start:end
                    ]


                    cards = json.loads(
                        cleaned
                    )


                    st.session_state.flashcards = cards


                    st.success(
                        "🎉 Flashcards generated!"
                    )


                    save_study_activity()


                except Exception:

                    st.error(
                        "Could not generate flashcards. Please try again."
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
                f"🃏 Card {i + 1} — {card['question']}"
            ):

                st.markdown(
                    "### 💡 Answer"
                )

                st.write(
                    card["answer"]
                )


# =========================================================
# PROGRESS TRACKER
# =========================================================

elif page == "Progress Tracker":

    st.title(
        "📊 Progress Tracker"
    )

    st.write(
        "Track your learning journey with StudySync."
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


    st.subheader(
        "🔥 Current Study Streak"
    )


    st.metric(
        "Days",
        streak
    )


    st.progress(
        min(
            streak / 30,
            1.0
        )
    )


    st.divider()


    st.subheader(
        "📝 Recent Quiz History"
    )


    history = get_quiz_history()


    if history:

        for quiz in history:

            percentage = quiz[
                "percentage"
            ]


            st.markdown(
                f"""
                <div class="feature-card">

                    <div style="
                        font-size:1.05rem;
                        font-weight:700;
                    ">
                        🧠 {quiz["topic"]}
                    </div>

                    <div style="
                        color:#aeb8d4;
                        margin-top:6px;
                    ">
                        Score:
                        {quiz["score"]}/{quiz["total"]}
                        &nbsp; • &nbsp;
                        {percentage}%
                        &nbsp; • &nbsp;
                        {quiz["date"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    else:

        st.info(
            "No quiz history yet. Start your first quiz!"
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#66708f;
        padding:35px 0 10px 0;
        font-size:0.8rem;
    ">

        StudySync • Learn Smarter 🚀

    </div>
    """,
    unsafe_allow_html=True
)
