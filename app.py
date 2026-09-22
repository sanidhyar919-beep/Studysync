import streamlit as st
from pypdf import PdfReader
from openai import OpenAI


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

if "quizzes_completed" not in st.session_state:
    st.session_state.quizzes_completed = 0

if "topics_completed" not in st.session_state:
    st.session_state.topics_completed = 0

if "study_progress" not in st.session_state:
    st.session_state.study_progress = 0

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []


# =========================================================
# GROQ AI CONNECTION
# =========================================================

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)


def ask_ai(prompt):

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        return (
            "AI connection failed\n\n"
            f"{type(e).__name__}: {e}"
        )


# =========================================================
# HOME PAGE
# =========================================================

if st.session_state.page == "Home":

    st.title("📚 StudySync")

    st.subheader(
        "Your AI Powered Study Companion"
    )

    st.write(
        "Study smarter with AI-powered notes, quizzes, "
        "flashcards and study assistance."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📄 Study Material",
            use_container_width=True
        ):
            st.session_state.page = "Study Material"
            st.rerun()

    with col2:

        if st.button(
            "🤖 AI Study Assistant",
            use_container_width=True
        ):
            st.session_state.page = "AI Study Assistant"
            st.rerun()

    with col3:

        if st.button(
            "📝 AI Notes Generator",
            use_container_width=True
        ):
            st.session_state.page = "AI Notes Generator"
            st.rerun()

    col4, col5, col6 = st.columns(3)

    with col4:

        if st.button(
            "🎯 AI Quiz Generator",
            use_container_width=True
        ):
            st.session_state.page = "AI Quiz Generator"
            st.rerun()

    with col5:

        if st.button(
            "🗂️ Flashcards",
            use_container_width=True
        ):
            st.session_state.page = "Flashcards"
            st.rerun()

    with col6:

        if st.button(
            "📊 Progress Tracker",
            use_container_width=True
        ):
            st.session_state.page = "Progress Tracker"
            st.rerun()


# =========================================================
# STUDY MATERIAL
# =========================================================

elif st.session_state.page == "Study Material":

    st.title("📄 Study Material")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    uploaded_file = st.file_uploader(
        "Upload your study material",
        type=["pdf"]
    )

    if uploaded_file:

        try:

            reader = PdfReader(uploaded_file)

            text = ""

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            st.success("PDF uploaded successfully!")

            with st.expander("📖 Extracted Text"):

                st.write(text[:12000])

            if st.button("🤖 Generate AI Notes"):

                with st.spinner("Generating notes..."):

                    prompt = f"""
Create simple and clear study notes from the following
study material.

Use:
- Important headings
- Bullet points
- Definitions
- Examples
- Important exam points

Study Material:

{text[:12000]}
"""

                    notes = ask_ai(prompt)

                st.subheader("📚 AI Generated Notes")

                st.write(notes)

        except Exception as e:

            st.error(
                f"Could not read the PDF: {e}"
            )


# =========================================================
# AI STUDY ASSISTANT
# =========================================================

elif st.session_state.page == "AI Study Assistant":

    st.title("🤖 AI Study Assistant")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    question = st.text_area(
        "Ask your study question:",
        placeholder="Example: Explain Big Data in simple words."
    )

    if st.button("Ask AI"):

        if question.strip() == "":

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner("AI is thinking..."):

                prompt = f"""
You are a helpful college study assistant.

Explain the following question in simple,
easy-to-understand language.

Use examples wherever useful.

Question:
{question}
"""

                answer = ask_ai(prompt)

            st.subheader("💡 AI Answer")

            st.write(answer)


# =========================================================
# AI NOTES GENERATOR
# =========================================================

elif st.session_state.page == "AI Notes Generator":

    st.title("📝 AI Notes Generator")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    topic = st.text_input(
        "Enter topic:",
        placeholder="Example: Machine Learning"
    )

    if st.button("Generate Notes"):

        if topic.strip() == "":

            st.warning(
                "Please enter a topic."
            )

        else:

            with st.spinner("Generating notes..."):

                prompt = f"""
Create detailed but easy-to-understand college notes
on the topic:

{topic}

Include:

1. Definition
2. Main concepts
3. Important points
4. Real-life examples
5. Advantages
6. Disadvantages
7. Exam-oriented points

Use simple language.
"""

                notes = ask_ai(prompt)

            st.subheader("📚 Generated Notes")

            st.write(notes)


# =========================================================
# AI QUIZ GENERATOR
# =========================================================

elif st.session_state.page == "AI Quiz Generator":

    st.title("🎯 AI Quiz Generator")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    topic = st.text_input(
        "Enter quiz topic:",
        placeholder="Example: Data Science"
    )

    number_of_questions = st.selectbox(
        "Number of Questions",
        [5, 10]
    )

    # -----------------------------------------------------
    # GENERATE QUIZ
    # -----------------------------------------------------

    if st.button("Generate Quiz"):

        if topic.strip() == "":

            st.warning(
                "Please enter a topic."
            )

        else:

            with st.spinner("Generating quiz..."):

                prompt = f"""
Create exactly {number_of_questions}
multiple-choice questions for college students.

Topic:
{topic}

Use EXACTLY this format:

QUESTION: question text
A: option A
B: option B
C: option C
D: option D
ANSWER: A

The ANSWER must contain only:
A, B, C or D.

Make the questions educational,
clear and different from each other.
"""

                quiz_text = ask_ai(prompt)

            # ---------------------------------------------
            # PARSE QUIZ
            # ---------------------------------------------

            lines = quiz_text.splitlines()

            questions = []

            current = {}

            for line in lines:

                line = line.strip()

                if line.startswith("QUESTION:"):

                    if current.get("question"):

                        questions.append(current)

                    current = {
                        "question":
                        line.replace(
                            "QUESTION:",
                            ""
                        ).strip()
                    }

                elif line.startswith("A:"):

                    current["A"] = line[2:].strip()

                elif line.startswith("B:"):

                    current["B"] = line[2:].strip()

                elif line.startswith("C:"):

                    current["C"] = line[2:].strip()

                elif line.startswith("D:"):

                    current["D"] = line[2:].strip()

                elif line.startswith("ANSWER:"):

                    current["answer"] = (
                        line.replace(
                            "ANSWER:",
                            ""
                        )
                        .strip()
                        .upper()
                    )

            if current.get("question"):

                questions.append(current)

            # ---------------------------------------------
            # VALID QUESTIONS
            # ---------------------------------------------

            valid_questions = []

            for q in questions:

                if (
                    q.get("question")
                    and q.get("A")
                    and q.get("B")
                    and q.get("C")
                    and q.get("D")
                    and q.get("answer")
                    in ["A", "B", "C", "D"]
                ):

                    valid_questions.append(q)

            # ---------------------------------------------
            # RETRY IF QUESTIONS ARE MISSING
            # ---------------------------------------------

            attempts = 0

            while (
                len(valid_questions)
                < number_of_questions
                and attempts < 3
            ):

                attempts += 1

                missing = (
                    number_of_questions
                    - len(valid_questions)
                )

                retry_prompt = f"""
Create exactly {missing}
additional multiple-choice questions
on the topic:

{topic}

Do not repeat previous questions.

Use EXACTLY this format:

QUESTION: question text
A: option A
B: option B
C: option C
D: option D
ANSWER: A

ANSWER must only be A, B, C or D.
"""

                retry_text = ask_ai(
                    retry_prompt
                )

                retry_lines = (
                    retry_text.splitlines()
                )

                current = {}

                for line in retry_lines:

                    line = line.strip()

                    if line.startswith("QUESTION:"):

                        if current.get("question"):

                            questions.append(
                                current
                            )

                        current = {
                            "question":
                            line.replace(
                                "QUESTION:",
                                ""
                            ).strip()
                        }

                    elif line.startswith("A:"):

                        current["A"] = (
                            line[2:].strip()
                        )

                    elif line.startswith("B:"):

                        current["B"] = (
                            line[2:].strip()
                        )

                    elif line.startswith("C:"):

                        current["C"] = (
                            line[2:].strip()
                        )

                    elif line.startswith("D:"):

                        current["D"] = (
                            line[2:].strip()
                        )

                    elif line.startswith("ANSWER:"):

                        current["answer"] = (
                            line.replace(
                                "ANSWER:",
                                ""
                            )
                            .strip()
                            .upper()
                        )

                if current.get("question"):

                    questions.append(current)

                valid_questions = []

                for q in questions:

                    if (
                        q.get("question")
                        and q.get("A")
                        and q.get("B")
                        and q.get("C")
                        and q.get("D")
                        and q.get("answer")
                        in ["A", "B", "C", "D"]
                    ):

                        valid_questions.append(q)

            # ---------------------------------------------
            # SAVE QUIZ IN SESSION
            # ---------------------------------------------

            st.session_state.quiz_questions = (
                valid_questions[
                    :number_of_questions
                ]
            )

            st.session_state.quiz_score = None

    # -----------------------------------------------------
    # DISPLAY QUIZ
    # -----------------------------------------------------

    if st.session_state.quiz_questions:

        questions = (
            st.session_state.quiz_questions
        )

        st.success(
            f"Generated {len(questions)} questions."
        )

        # FORM
        with st.form("quiz_form"):

            for i, q in enumerate(questions):

                st.markdown(
                    f"### Question {i + 1}"
                )

                st.write(
                    q["question"]
                )

                st.radio(
                    "Choose your answer:",
                    [
                        q["A"],
                        q["B"],
                        q["C"],
                        q["D"]
                    ],
                    key=f"quiz_answer_{i}"
                )

            submitted = (
                st.form_submit_button(
                    "✅ Submit Quiz"
                )
            )

        # -------------------------------------------------
        # SUBMIT QUIZ
        # -------------------------------------------------

        if submitted:

            score = 0

            for i, q in enumerate(
                questions
            ):

                selected = (
                    st.session_state[
                        f"quiz_answer_{i}"
                    ]
                )

                correct_option = q[
                    q["answer"]
                ]

                if selected == correct_option:

                    score += 1

            total = len(questions)

            percentage = (
                score / total
            ) * 100

            # ---------------------------------------------
            # UPDATE PROGRESS
            # ---------------------------------------------

            st.session_state.quizzes_completed += 1

            st.session_state.topics_completed += 1

            st.session_state.study_progress = min(
                100,
                st.session_state.study_progress + 5
            )

            st.session_state.quiz_score = (
                score,
                total,
                percentage
            )

        # -------------------------------------------------
        # QUIZ RESULT
        # -------------------------------------------------

        if st.session_state.quiz_score is not None:

            score, total, percentage = (
                st.session_state.quiz_score
            )

            st.divider()

            st.subheader(
                "🏆 Quiz Result"
            )

            st.metric(
                "Score",
                f"{score}/{total}"
            )

            st.progress(
                percentage / 100
            )

            st.write(
                f"Percentage: {percentage:.1f}%"
            )

            if percentage >= 80:

                st.success(
                    "Excellent work! 🎉"
                )

            elif percentage >= 50:

                st.info(
                    "Good job! Keep practicing. 👍"
                )

            else:

                st.warning(
                    "Keep studying and try again. 💪"
                )

            # ---------------------------------------------
            # ANSWER REVIEW
            # ---------------------------------------------

            st.subheader(
                "📋 Answer Review"
            )

            for i, q in enumerate(
                questions
            ):

                selected = (
                    st.session_state[
                        f"quiz_answer_{i}"
                    ]
                )

                correct_option = q[
                    q["answer"]
                ]

                if selected == correct_option:

                    st.success(
                        f"Question {i + 1}: "
                        "Correct ✅"
                    )

                else:

                    st.error(
                        f"Question {i + 1}: "
                        f"Your answer: {selected} | "
                        f"Correct answer: "
                        f"{correct_option}"
                    )


# =========================================================
# FLASHCARDS
# =========================================================

elif st.session_state.page == "Flashcards":

    st.title("🗂️ AI Flashcards")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    topic = st.text_input(
        "Enter topic for flashcards:",
        placeholder="Example: Python"
    )

    number_of_cards = st.selectbox(
        "Number of Flashcards",
        [5, 10]
    )

    if st.button("Generate Flashcards"):

        if topic.strip() == "":

            st.warning(
                "Please enter a topic."
            )

        else:

            with st.spinner(
                "Generating flashcards..."
            ):

                prompt = f"""
Create {number_of_cards}
study flashcards on:

{topic}

Use this format:

Q: question
A: answer

Keep answers short and useful
for college students.
"""

                flashcard_text = ask_ai(
                    prompt
                )

            # ---------------------------------------------
            # PARSE FLASHCARDS
            # ---------------------------------------------

            lines = (
                flashcard_text.splitlines()
            )

            cards = []

            current_question = None

            for line in lines:

                line = line.strip()

                if line.startswith("Q:"):

                    current_question = (
                        line[2:].strip()
                    )

                elif (
                    line.startswith("A:")
                    and current_question
                ):

                    answer = (
                        line[2:].strip()
                    )

                    cards.append(
                        (
                            current_question,
                            answer
                        )
                    )

                    current_question = None

            st.session_state.flashcards = (
                cards[:number_of_cards]
            )

    # ---------------------------------------------
    # DISPLAY FLASHCARDS
    # ---------------------------------------------

    if st.session_state.flashcards:

        st.success(
            f"Generated "
            f"{len(st.session_state.flashcards)} "
            "flashcards."
        )

        for i, card in enumerate(
            st.session_state.flashcards
        ):

            question, answer = card

            with st.expander(
                f"Card {i + 1}: {question}"
            ):

                st.write(
                    f"**Answer:** {answer}"
                )


# =========================================================
# PROGRESS TRACKER
# =========================================================

elif st.session_state.page == "Progress Tracker":

    st.title("📊 Progress Tracker")

    st.write(
        "Track your study progress."
    )

    if st.button("⬅️ Back"):

        st.session_state.page = "Home"

        st.rerun()

    st.divider()

    # ---------------------------------------------
    # STUDY PROGRESS
    # ---------------------------------------------

    progress = (
        st.session_state.study_progress
    )

    st.subheader(
        "Study Progress"
    )

    st.progress(
        progress / 100
    )

    st.metric(
        "Study Progress",
        f"{progress}%"
    )

    # ---------------------------------------------
    # STATISTICS
    # ---------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Topics Completed",
            st.session_state.topics_completed
        )

    with col2:

        st.metric(
            "Quizzes Completed",
            st.session_state.quizzes_completed
        )

    st.metric(
        "Current Streak",
        "5 Days"
    )

    st.divider()

    st.info(
        "Complete quizzes regularly to increase "
        "your study progress."
    )
