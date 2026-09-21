import streamlit as st
from pypdf import PdfReader
from openai import OpenAI


# ==============================
# OLLAMA AI CONNECTION
# ==============================

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)


def ask_ai(prompt):
    """Send a question to local Ollama AI."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b"
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ==============================
# PAGE SETTINGS
# ==============================

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide"
)


# ==============================
# PAGE STATE
# ==============================

if "page" not in st.session_state:
    st.session_state.page = "Home"


# ==============================
# HOME PAGE
# ==============================

if st.session_state.page == "Home":

    st.title("📚 StudySync")
    st.subheader("Your AI-Powered Study Assistant")

    st.write(
        "StudySync helps students study smarter with "
        "study material, AI notes, quizzes, flashcards "
        "and progress tracking."
    )

    st.divider()

    # ==============================
    # TEST AI
    # ==============================

    if st.button("🧪 Test AI"):

        try:

            response = client.chat.completions.create(
                model="llama3.2",
                messages=[
                    {
                        "role": "user",
                        "content":
                        "Say 'StudySync AI connected successfully!'"
                    }
                ]
            )

            st.success(
                response.choices[0].message.content
            )

        except Exception as e:

            st.error("AI connection failed")
            st.write(e)

    st.header("What do you want to study?")

    # ==============================
    # ROW 1
    # ==============================

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📚 Study Material",
            use_container_width=True,
            key="home_study"
        ):

            st.session_state.page = "Study Material"
            st.rerun()

    with col2:

        if st.button(
            "🤖 AI Study Assistant",
            use_container_width=True,
            key="home_ai"
        ):

            st.session_state.page = "AI Study Assistant"
            st.rerun()

    with col3:

        if st.button(
            "📝 Notes Generator",
            use_container_width=True,
            key="home_notes"
        ):

            st.session_state.page = "Notes Generator"
            st.rerun()


    # ==============================
    # ROW 2
    # ==============================

    col4, col5, col6 = st.columns(3)

    with col4:

        if st.button(
            "🎯 Quiz Generator",
            use_container_width=True,
            key="home_quiz"
        ):

            st.session_state.page = "Quiz Generator"
            st.rerun()

    with col5:

        if st.button(
            "🃏 Flashcards",
            use_container_width=True,
            key="home_flashcards"
        ):

            st.session_state.page = "Flashcards"
            st.rerun()

    with col6:

        if st.button(
            "📊 Progress Tracker",
            use_container_width=True,
            key="home_progress"
        ):

            st.session_state.page = "Progress Tracker"
            st.rerun()


# =========================================================
# STUDY MATERIAL PAGE
# =========================================================

elif st.session_state.page == "Study Material":

    st.title("📚 Study Material")

    st.write("Upload your study PDF here.")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="study_pdf"
    )

    if uploaded_file:

        st.success("PDF uploaded successfully! ✅")

        try:

            reader = PdfReader(uploaded_file)

            text = ""

            for page in reader.pages:

                text += page.extract_text() or ""

            if text.strip():

                st.subheader("📄 Extracted Study Material")

                st.text_area(
                    "PDF Content",
                    text,
                    height=300,
                    key="pdf_text"
                )

                st.divider()

                # ==============================
                # AI NOTES FROM PDF
                # ==============================

                if st.button(
                    "🤖 Generate AI Notes",
                    key="generate_pdf_notes"
                ):

                    with st.spinner(
                        "AI is reading your PDF..."
                    ):

                        try:

                            prompt = f"""
You are a helpful college study assistant.

Read the following study material and create
simple, exam-friendly notes.

Use:
- Clear headings
- Bullet points
- Important definitions
- Important concepts
- Simple examples

Study Material:

{text[:12000]}
"""

                            notes = ask_ai(prompt)

                            st.subheader(
                                "📝 AI Generated Study Notes"
                            )

                            st.write(notes)

                        except Exception as e:

                            st.error(
                                "AI could not generate notes."
                            )

                            st.write(e)

            else:

                st.warning(
                    "Text could not be extracted from this PDF."
                )

        except Exception as e:

            st.error(
                "There was a problem reading the PDF."
            )

            st.write(e)

    st.divider()

    if st.button(
        "⬅️ Back",
        key="back_study"
    ):

        st.session_state.page = "Home"
        st.rerun()


# =========================================================
# AI STUDY ASSISTANT
# =========================================================

elif st.session_state.page == "AI Study Assistant":

    st.title("🤖 AI Study Assistant")

    st.write(
        "Ask any study-related question and get an AI answer."
    )

    question = st.text_area(
        "Enter your question:",
        placeholder="Example: Explain pointers in C in simple language.",
        key="ai_question"
    )

    if st.button(
        "🤖 Ask AI",
        key="ask_ai"
    ):

        if question:

            with st.spinner(
                "AI is thinking..."
            ):

                try:

                    prompt = f"""
You are StudySync, an AI study assistant
for college students.

Answer the student's question in simple language.

Give:
1. Simple explanation
2. Important points
3. Real-life example if useful
4. Exam point of view

Student Question:

{question}
"""

                    answer = ask_ai(prompt)

                    st.subheader("🤖 AI Answer")

                    st.write(answer)

                except Exception as e:

                    st.error(
                        "AI connection failed."
                    )

                    st.write(e)

        else:

            st.warning(
                "Please enter a question."
            )

    st.divider()

    if st.button(
        "⬅️ Back",
        key="back_ai"
    ):

        st.session_state.page = "Home"
        st.rerun()


# =========================================================
# NOTES GENERATOR
# =========================================================

elif st.session_state.page == "Notes Generator":

    st.title("📝 AI Notes Generator")

    st.write(
        "Enter a topic and generate simple AI study notes."
    )

    topic = st.text_input(
        "Enter topic:",
        placeholder="Example: Data Science",
        key="notes_topic"
    )

    if st.button(
        "🤖 Generate Notes",
        key="generate_notes"
    ):

        if topic:

            with st.spinner(
                "Generating notes..."
            ):

                try:

                    prompt = f"""
Create simple and exam-friendly notes
for a college student on the topic:

{topic}

Include:

1. Introduction
2. Definition
3. Important concepts
4. Key points
5. Real-life example
6. Advantages if applicable
7. Conclusion

Use simple language.
"""

                    notes = ask_ai(prompt)

                    st.subheader(
                        f"📖 Notes: {topic}"
                    )

                    st.write(notes)

                except Exception as e:

                    st.error(
                        "Could not generate notes."
                    )

                    st.write(e)

        else:

            st.warning(
                "Please enter a topic."
            )

    st.divider()

    if st.button(
        "⬅️ Back",
        key="back_notes"
    ):

        st.session_state.page = "Home"
        st.rerun()
# =========================================================
# QUIZ GENERATOR
# =========================================================

elif st.session_state.page == "Quiz Generator":

    st.title("🎯 AI Quiz Generator")

    st.write(
        "Create an interactive MCQ quiz using AI."
    )

    # =====================================================
    # QUIZ SETTINGS
    # =====================================================

    topic = st.text_input(
        "📚 Enter quiz topic:",
        placeholder="Example: C Programming"
    )

    col1, col2 = st.columns(2)

    with col1:

        difficulty = st.selectbox(
            "🎯 Difficulty:",
            ["Easy", "Medium", "Hard"]
        )

    with col2:

        number = st.selectbox(
            "📝 Number of Questions:",
            [5, 10]
        )

    # =====================================================
    # GENERATE QUIZ BUTTON
    # =====================================================

    if st.button(
        "🚀 Generate Quiz",
        use_container_width=True
    ):

        if topic.strip() == "":

            st.warning(
                "⚠️ Please enter a topic first."
            )

        else:

            questions = []

            # =================================================
            # FUNCTION TO PARSE AI QUESTIONS
            # =================================================

            def parse_questions(response):

                parsed_questions = []

                # ---------------------------------------------
                # Split using QUESTION:
                # ---------------------------------------------

                blocks = response.split(
                    "QUESTION:"
                )

                for block in blocks[1:]:

                    lines = [
                        line.strip()
                        for line in block.splitlines()
                        if line.strip()
                    ]

                    if len(lines) < 6:
                        continue

                    question_text = lines[0]

                    option_a = ""
                    option_b = ""
                    option_c = ""
                    option_d = ""
                    answer = ""

                    # -----------------------------------------
                    # Read every line
                    # -----------------------------------------

                    for line in lines[1:]:

                        upper = line.upper()

                        if upper.startswith("A:"):

                            option_a = line.split(
                                ":",
                                1
                            )[1].strip()

                        elif upper.startswith("B:"):

                            option_b = line.split(
                                ":",
                                1
                            )[1].strip()

                        elif upper.startswith("C:"):

                            option_c = line.split(
                                ":",
                                1
                            )[1].strip()

                        elif upper.startswith("D:"):

                            option_d = line.split(
                                ":",
                                1
                            )[1].strip()

                        elif upper.startswith(
                            "ANSWER:"
                        ):

                            answer = line.split(
                                ":",
                                1
                            )[1].strip().upper()

                    # -----------------------------------------
                    # Validate question
                    # -----------------------------------------

                    if (
                        question_text
                        and option_a
                        and option_b
                        and option_c
                        and option_d
                        and answer in [
                            "A",
                            "B",
                            "C",
                            "D"
                        ]
                    ):

                        answer_index = {
                            "A": 0,
                            "B": 1,
                            "C": 2,
                            "D": 3
                        }[answer]

                        parsed_questions.append(
                            {
                                "question": question_text,

                                "options": [
                                    option_a,
                                    option_b,
                                    option_c,
                                    option_d
                                ],

                                "answer": answer_index
                            }
                        )

                return parsed_questions

            # =================================================
            # FIRST AI REQUEST
            # =================================================

            prompt = f"""
You are an AI quiz generator for college students.

Create exactly {number} multiple choice questions.

Topic: {topic}

Difficulty: {difficulty}

You MUST follow this exact format for EVERY question:

QUESTION: Question text
A: Option A
B: Option B
C: Option C
D: Option D
ANSWER: A

Example:

QUESTION: What is a variable in C?
A: A storage location
B: A compiler
C: An operating system
D: A database
ANSWER: A

QUESTION: Which symbol is used to end a C statement?
A: :
B: ;
C: .
D: ,
ANSWER: B

IMPORTANT RULES:

1. Create exactly {number} questions.
2. Every question must have exactly four options.
3. Options must be A, B, C and D.
4. ANSWER must be only A, B, C or D.
5. Do not explain the answers.
6. Do not use markdown.
7. Do not add introductions.
8. Do not add conclusions.
"""

            with st.spinner(
                "🤖 AI is creating your quiz..."
            ):

                try:

                    response = ask_ai(
                        prompt
                    )

                    # -----------------------------------------
                    # Parse first response
                    # -----------------------------------------

                    questions = parse_questions(
                        response
                    )

                    # -----------------------------------------
                    # Show raw response
                    # -----------------------------------------

                    with st.expander(
                        "🔍 See AI Response"
                    ):

                        st.code(
                            response
                        )

                    # =================================================
                    # GENERATE MISSING QUESTIONS
                    # =================================================

                    attempts = 0

                    max_attempts = 5

                    while (
                        len(questions) < number
                        and attempts < max_attempts
                    ):

                        missing = (
                            number
                            - len(questions)
                        )

                        attempts += 1

                        st.info(
                            f"🔄 Generating "
                            f"{missing} missing question(s)..."
                        )

                        extra_prompt = f"""
You are creating missing questions for a college quiz.

Topic: {topic}

Difficulty: {difficulty}

We already have some questions.

We need exactly {missing} NEW questions.

Use EXACTLY this format:

QUESTION: Question text
A: Option A
B: Option B
C: Option C
D: Option D
ANSWER: A

IMPORTANT:

- Create exactly {missing} questions.
- Do not repeat previous questions.
- Every question must have A, B, C and D.
- ANSWER must be A, B, C or D.
- Do not explain anything.
- Do not use markdown.
"""

                        extra_response = ask_ai(
                            extra_prompt
                        )

                        extra_questions = parse_questions(
                            extra_response
                        )

                        # -----------------------------------------
                        # Add new questions
                        # -----------------------------------------

                        for q in extra_questions:

                            if len(questions) >= number:
                                break

                            questions.append(q)

                        # -----------------------------------------
                        # Show extra response
                        # -----------------------------------------

                        with st.expander(
                            f"🔍 AI Retry {attempts}"
                        ):

                            st.code(
                                extra_response
                            )

                    # =================================================
                    # FINAL CHECK
                    # =================================================

                    if len(questions) >= number:

                        # Keep only required number
                        questions = questions[:number]

                        # Save quiz
                        st.session_state.quiz_data = (
                            questions
                        )

                        st.session_state.quiz_topic = (
                            topic
                        )

                        st.session_state.quiz_generated = (
                            True
                        )

                        st.session_state.quiz_submitted = (
                            False
                        )

                        st.session_state.quiz_score = (
                            0
                        )

                        st.session_state.user_answers = {}

                        st.success(
                            f"🎉 {number} questions "
                            f"generated successfully!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"⚠️ AI generated only "
                            f"{len(questions)} valid "
                            f"questions out of {number}."
                        )

                        st.info(
                            "Try generating the quiz again."
                        )

                except Exception as e:

                    st.error(
                        "❌ Something went wrong."
                    )

                    st.exception(e)

    # =====================================================
    # DISPLAY QUIZ
    # =====================================================

    if st.session_state.get(
        "quiz_generated",
        False
    ):

        st.divider()

        st.subheader(
            f"🎯 {st.session_state.quiz_topic} Quiz"
        )

        quiz_data = (
            st.session_state.quiz_data
        )

        # =================================================
        # QUESTIONS
        # =================================================

        for i, q in enumerate(
            quiz_data
        ):

            st.markdown(
                f"### Question {i + 1}"
            )

            st.write(
                q["question"]
            )

            selected_answer = st.radio(
                "Choose your answer:",
                q["options"],
                index=None,
                key=f"quiz_answer_{i}"
            )

            st.session_state.user_answers[i] = (
                selected_answer
            )

            st.divider()

        # =================================================
        # SUBMIT QUIZ
        # =================================================

        if st.button(
            "✅ Submit Quiz",
            use_container_width=True
        ):

            score = 0

            for i, q in enumerate(
                quiz_data
            ):

                user_answer = (
                    st.session_state.user_answers.get(
                        i
                    )
                )

                correct_answer = (
                    q["options"][
                        q["answer"]
                    ]
                )

                if (
                    user_answer
                    == correct_answer
                ):

                    score += 1

            st.session_state.quiz_score = (
                score
            )

            st.session_state.quiz_submitted = (
                True
            )

            st.rerun()

        # =================================================
        # RESULT
        # =================================================

        if st.session_state.get(
            "quiz_submitted",
            False
        ):

            score = (
                st.session_state.quiz_score
            )

            total = len(
                quiz_data
            )

            percentage = int(
                (score / total) * 100
            )

            st.divider()

            st.subheader(
                "📊 Quiz Result"
            )

            # ---------------------------------------------
            # Score
            # ---------------------------------------------

            st.metric(
                "Your Score",
                f"{score} / {total}"
            )

            # ---------------------------------------------
            # Percentage
            # ---------------------------------------------

            st.progress(
                percentage / 100
            )

            st.write(
                f"### 📈 Percentage: {percentage}%"
            )

            # ---------------------------------------------
            # Result message
            # ---------------------------------------------

            if percentage >= 80:

                st.success(
                    "🔥 Excellent! "
                    "Very good performance!"
                )

            elif percentage >= 50:

                st.info(
                    "👍 Good job! "
                    "Keep practicing."
                )

            else:

                st.warning(
                    "📚 Keep studying "
                    "and try again."
                )

            # =================================================
            # ANSWER REVIEW
            # =================================================

            st.divider()

            st.subheader(
                "📖 Answer Review"
            )

            for i, q in enumerate(
                quiz_data
            ):

                user_answer = (
                    st.session_state.user_answers.get(
                        i
                    )
                )

                correct_answer = (
                    q["options"][
                        q["answer"]
                    ]
                )

                st.write(
                    f"**Q{i + 1}. "
                    f"{q['question']}**"
                )

                if (
                    user_answer
                    == correct_answer
                ):

                    st.success(
                        f"✅ Correct Answer: "
                        f"{correct_answer}"
                    )

                else:

                    st.error(
                        f"❌ Your Answer: "
                        f"{user_answer if user_answer else 'Not answered'}"
                    )

                    st.info(
                        f"✅ Correct Answer: "
                        f"{correct_answer}"
                    )

                st.divider()

    # =====================================================
    # BACK BUTTON
    # =====================================================

    if st.button(
        "⬅️ Back"
    ):

        st.session_state.page = "Home"

        st.rerun()
# =========================================================
# FLASHCARDS
# =========================================================

elif st.session_state.page == "Flashcards":

    st.title("🃏 AI Flashcards")

    st.write(
        "Generate quick revision flashcards using AI."
    )

    topic = st.text_input(
        "Enter topic:",
        key="flashcard_topic"
    )

    if st.button(
        "🃏 Generate Flashcards",
        key="generate_flashcards"
    ):

        if topic:

            with st.spinner(
                "Creating flashcards..."
            ):

                try:

                    prompt = f"""
Create 10 useful flashcards for college students
on the topic:

{topic}

Format each flashcard as:

Flashcard 1
Question:
Answer:

Keep answers short and easy to revise.
"""

                    cards = ask_ai(prompt)

                    st.subheader(
                        f"🃏 Flashcards: {topic}"
                    )

                    st.write(cards)

                except Exception as e:

                    st.error(
                        "Could not generate flashcards."
                    )

                    st.write(e)

        else:

            st.warning(
                "Please enter a topic."
            )

    st.divider()

    if st.button(
        "⬅️ Back",
        key="back_flashcards"
    ):

        st.session_state.page = "Home"
        st.rerun()


# =========================================================
# PROGRESS TRACKER
# =========================================================

elif st.session_state.page == "Progress Tracker":

    st.title("📊 Progress Tracker")

    st.subheader(
        "Your Study Progress"
    )

    st.metric(
        "Study Progress",
        "65%"
    )

    st.progress(0.65)

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📚 Topics Completed",
            "13"
        )

    with col2:

        st.metric(
            "🎯 Quizzes Completed",
            "8"
        )

    with col3:

        st.metric(
            "🔥 Current Streak",
            "5 Days"
        )

    st.divider()

    st.write(
        "Keep studying regularly to improve your progress! 🚀"
    )

    if st.button(
        "⬅️ Back",
        key="back_progress"
    ):

        st.session_state.page = "Home"
        st.rerun()
