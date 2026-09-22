import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from pypdf import PdfReader
from supabase import create_client
from datetime import date, timedelta
import json
import re
import time


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
# SESSION STATE
# =========================================================

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []


# =========================================================
# MAIN APP CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
        radial-gradient(
            circle at 10% 10%,
            rgba(88, 80, 255, 0.14),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(0, 200, 255, 0.08),
            transparent 28%
        ),
        #070a14;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background: #080b17;
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    h2,
    h3 {
        color: #ffffff !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 20px;
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: rgba(100,120,255,0.40);
        box-shadow:
            0 12px 35px rgba(60,70,255,0.15);
    }

    div[data-testid="stMetricLabel"] {
        color: #9da8c4 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    .stButton > button {
        width: 100%;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1rem;
        color: #ffffff;
        font-weight: 700;
        background:
            linear-gradient(
                90deg,
                #5865f2,
                #7957e8
            );
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow:
            0 10px 30px rgba(88,101,242,0.30);
    }

    .stTextInput input,
    .stTextArea textarea {
        background: rgba(255,255,255,0.045) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
    }

    div[data-testid="stProgressBar"] > div > div {
        background:
            linear-gradient(
                90deg,
                #5865f2,
                #8b5cf6,
                #55dfff
            );
    }

    .home-title {
        font-size: 3rem;
        font-weight: 800;
        background:
            linear-gradient(
                90deg,
                #ffffff,
                #9ba8ff,
                #5bdcff
            );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1.5px;
    }

    .home-subtitle {
        color: #9da8c4;
        font-size: 1.05rem;
        margin-top: 5px;
        margin-bottom: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# INTRO ANIMATION
# =========================================================

if not st.session_state.intro_done:

    components.html(
        """
        <!DOCTYPE html>

        <html>

        <head>

        <style>

        html,
        body {

            margin: 0;

            padding: 0;

            width: 100%;

            height: 100%;

            overflow: hidden;

        }

        body {

            background:
                radial-gradient(
                    circle at center,
                    #171c40 0%,
                    #090c1b 50%,
                    #05070f 100%
                );

            display: flex;

            align-items: center;

            justify-content: center;

            font-family:
                Arial,
                Helvetica,
                sans-serif;

        }

        .intro {

            text-align: center;

            animation:
                introIn
                1.2s
                cubic-bezier(.16,1,.3,1)
                forwards;

        }

        .logo {

            font-size: 72px;

            margin-bottom: 10px;

            animation:
                floating
                2s
                ease-in-out
                infinite;

        }

        .title {

            font-size: 58px;

            font-weight: 900;

            letter-spacing: -2px;

            background:
                linear-gradient(
                    90deg,
                    #ffffff,
                    #a5b0ff,
                    #55dfff
                );

            -webkit-background-clip: text;

            -webkit-text-fill-color: transparent;

        }

        .subtitle {

            margin-top: 14px;

            color: #8995b5;

            font-size: 14px;

            letter-spacing: 4px;

            text-transform: uppercase;

            opacity: 0;

            animation:
                subtitleIn
                1s
                ease
                0.5s
                forwards;

        }

        .line {

            width: 0;

            height: 2px;

            margin: 25px auto 0;

            border-radius: 10px;

            background:
                linear-gradient(
                    90deg,
                    #5865f2,
                    #8b5cf6,
                    #55dfff
                );

            animation:
                lineGrow
                1.2s
                ease
                0.8s
                forwards;

        }

        @keyframes introIn {

            0% {

                opacity: 0;

                transform:
                    translateY(35px)
                    scale(0.85);

            }

            100% {

                opacity: 1;

                transform:
                    translateY(0)
                    scale(1);

            }

        }

        @keyframes subtitleIn {

            0% {

                opacity: 0;

                transform:
                    translateY(12px);

            }

            100% {

                opacity: 1;

                transform:
                    translateY(0);

            }

        }

        @keyframes lineGrow {

            0% {

                width: 0;

            }

            100% {

                width: 180px;

            }

        }

        @keyframes floating {

            0%,
            100% {

                transform:
                    translateY(0);

            }

            50% {

                transform:
                    translateY(-10px);

            }

        }

        </style>

        </head>

        <body>

            <div class="intro">

                <div class="logo">
                    📚
                </div>

                <div class="title">
                    StudySync
                </div>

                <div class="subtitle">
                    AI Powered Study Companion
                </div>

                <div class="line"></div>

            </div>

        </body>

        </html>
        """,
        height=600,
        scrolling=False
    )

    time.sleep(3.5)

    st.session_state.intro_done = True

    st.rerun()


# =========================================================
# GROQ AI CLIENT
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
        .order(
            "id",
            desc=True
        )
        .limit(10)
        .execute()
    )

    return result.data


# =========================================================
# IMPROVED AI FUNCTION
# =========================================================

def ask_ai(prompt):

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",

                "content": """
You are StudySync, an advanced AI study assistant
designed to help college students learn concepts
clearly and effectively.

Your primary goal is understanding, not just answering.

FOLLOW THESE RULES:

1. UNDERSTAND THE QUESTION

- Carefully understand what the student is asking.
- Answer the exact question.
- Do not go off-topic.
- If the question is unclear, make a reasonable
  assumption and clearly mention it.

2. SIMPLE EXPLANATIONS

- Explain difficult concepts in simple,
  student-friendly language.
- Avoid unnecessary technical jargon.
- If a technical term is necessary,
  explain it immediately.
- Assume the student may be learning the topic
  for the first time.

3. STRUCTURE

When appropriate, organize answers using:

- Definition
- Explanation
- How it works
- Example
- Advantages
- Disadvantages
- Important points
- Exam points

Do not force every section when it is unnecessary.

4. REAL-LIFE EXAMPLES

- Use simple real-world examples whenever
  they make the concept easier to understand.
- Examples should actually relate to the concept.

5. EXAM-ORIENTED ANSWERS

For academic questions:

- Give a clear definition first.
- Explain the concept properly.
- Highlight important points.
- Add examples where useful.
- Make the answer suitable for college exams.
- If the student asks for a 5-mark or 10-mark answer,
  adjust the depth accordingly.

6. PROGRAMMING QUESTIONS

For programming questions:

- Give correct and runnable code when code is requested.
- Explain the important parts of the code.
- Keep explanations beginner-friendly.
- Point out common mistakes when useful.
- Do not provide unnecessarily complicated code.

7. MATHEMATICS AND LOGIC

- Solve step by step.
- Show the important calculation or reasoning.
- Check the final answer before giving it.
- Do not skip important steps in a multi-step problem.

8. ACCURACY

- Never intentionally invent facts.
- Do not create fake sources,
  statistics or references.
- If you are uncertain about something,
  clearly say so instead of presenting it as certain.
- Distinguish facts from assumptions.

9. RESPONSE LENGTH

- Give enough detail to properly understand the topic.
- Do not make answers unnecessarily long.
- For simple questions, give simple answers.
- For difficult questions, provide deeper explanations.
- Match the response length to the student's question.

10. READABILITY

- Use headings and bullet points when helpful.
- Use short paragraphs.
- Bold important terms when appropriate.
- Keep the answer visually easy to study.

11. LEARNING FIRST

- Whenever possible, explain WHY something works,
  not just WHAT it is.
- Help the student understand the concept instead
  of blindly memorizing it.

12. COMPARISONS

When comparing two concepts:

- Explain both concepts separately.
- Then provide a clear comparison.
- Use a table when it improves understanding.

13. REVISION

When the student asks for revision material:

- Keep it concise.
- Highlight important exam points.
- Include definitions and key differences.
- Add examples when useful.

14. TONE

- Be friendly, supportive and patient.
- Never make the student feel bad for asking
  a basic question.
- Respond like a knowledgeable tutor.

15. DO NOT REPEAT

- Avoid repeating the same point in multiple ways
  unless repetition is specifically useful for learning.

16. NO UNNECESSARY FILLER

- Do not start every response with phrases like
  "Sure!" or "Absolutely!".
- Go directly to the useful explanation when possible.

17. FINAL QUALITY CHECK

Before answering, mentally check:

- Did I answer the actual question?
- Is the explanation accurate?
- Is it easy for a college student to understand?
- Did I include an example when useful?
- Did I avoid unnecessary information?

Your final answer should prioritize:

CLARITY + ACCURACY + UNDERSTANDING + USEFULNESS.
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

    st.markdown(
        '<div class="home-title">'
        'Welcome to StudySync 🚀'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="home-subtitle">'
        'Your intelligent AI-powered study companion. '
        'Learn smarter. Practice better. Track your progress.'
        '</div>',
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
                "AI is analyzing your PDF..."
            ):

                notes = ask_ai(
                    f"""
                    Create clear,
                    detailed and exam-oriented
                    notes from this study material.

                    Make the notes easy for a college
                    student to understand.

                    Include important definitions,
                    concepts, examples, key points
                    and likely exam points.

                    Study material:

                    {text[:15000]}
                    """
                )

            st.subheader(
                "📝 AI Generated Notes"
            )

            st.write(notes)

            save_study_activity()


# =========================================================
# AI STUDY ASSISTANT
# =========================================================

elif page == "🤖 AI Study Assistant":

    st.title(
        "🤖 AI Study Assistant"
    )

    st.write(
        "Ask anything related to your studies."
    )

    question = st.text_area(
        "💬 Your Question",
        placeholder=
        "Example: Explain pointers in C in simple language."
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

            st.subheader(
                "💡 Answer"
            )

            st.write(answer)

            save_study_activity()

        else:

            st.warning(
                "Please enter a question."
            )


# =========================================================
# AI NOTES GENERATOR
# =========================================================

elif page == "📝 AI Notes Generator":

    st.title(
        "📝 AI Notes Generator"
    )

    st.write(
        "Generate easy and exam-ready notes."
    )

    topic = st.text_input(
        "📚 Enter Topic",
        placeholder=
        "Example: Operating System"
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
                    Create detailed,
                    clear and exam-oriented
                    notes for:

                    {topic}

                    Explain everything in
                    simple student-friendly language.

                    Include:

                    1. Definition
                    2. Explanation
                    3. How it works
                    4. Important points
                    5. Real-life example
                    6. Advantages
                    7. Disadvantages
                    8. Important exam points
                    """
                )

            st.subheader(
                "📚 Your Notes"
            )

            st.write(notes)

            save_study_activity()

        else:

            st.warning(
                "Please enter a topic."
            )


# =========================================================
# AI QUIZ GENERATOR
# =========================================================

elif page == "🧠 AI Quiz Generator":

    st.title(
        "🧠 AI Quiz Generator"
    )

    st.write(
        "Generate a quiz and test your knowledge."
    )

    topic = st.text_input(
        "📚 Quiz Topic",
        placeholder=
        "Example: C Programming"
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
                "Generating quiz..."
            ):

                prompt = f"""
                Create {number} high-quality
                multiple choice questions
                about {topic}.

                Questions should test actual
                understanding, not just wording.

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

                Requirements:

                - Exactly {number} questions
                - Exactly 4 options per question
                - Exactly one correct answer
                - Plausible incorrect options
                - No duplicate questions
                - Accurate answers
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

                end = cleaned.rfind("]") + 1

                cleaned = cleaned[
                    start:end
                ]

                questions = json.loads(
                    cleaned
                )

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

        with st.form(
            "quiz_form"
        ):

            answers = []

            for i, question in enumerate(
                questions
            ):

                st.markdown(
                    f"### Q{i + 1}. "
                    f"{question['question']}"
                )

                selected = st.radio(
                    "Select answer:",
                    question["options"],
                    key=f"question_{i}"
                )

                answers.append(
                    selected
                )

            submitted = st.form_submit_button(
                "✅ Submit Quiz"
            )

        if submitted:

            score = 0

            for i, question in enumerate(
                questions
            ):

                if (
                    answers[i]
                    ==
                    question["answer"]
                ):

                    score += 1

            total = len(
                questions
            )

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
                f"🎉 Your score: "
                f"{score}/{total}"
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

            for i, question in enumerate(
                questions
            ):

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

    st.title(
        "🃏 AI Flashcards"
    )

    st.write(
        "Create quick revision cards using AI."
    )

    topic = st.text_input(
        "📚 Flashcard Topic",
        placeholder=
        "Example: Data Structures"
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
                Create {number}
                high-quality flashcards
                about {topic}.

                Focus on important concepts,
                definitions and exam-relevant facts.

                Return ONLY valid JSON.

                Format:

                [
                    {{
                        "question": "Question",
                        "answer": "Answer"
                    }}
                ]

                Requirements:

                - Exactly {number} cards
                - Clear questions
                - Accurate answers
                - No duplicate cards
                - Easy to revise
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

                end = cleaned.rfind("]") + 1

                cleaned = cleaned[
                    start:end
                ]

                cards = json.loads(
                    cleaned
                )

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
# PROGRESS TRACKER
# =========================================================

elif page == "📊 Progress Tracker":

    st.title(
        "📊 Progress Tracker"
    )

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

    st.subheader(
        "🔥 Current Streak"
    )

    st.metric(
        "Study Streak",
        f"{streak} Days"
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

            st.info(
                f"""
                🧠 **{quiz["topic"]}**

                Score:
                {quiz["score"]}/{quiz["total"]}

                Percentage:
                {quiz["percentage"]}%

                Date:
                {quiz["date"]}
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
