import streamlit as st
from pypdf import PdfReader
from openai import OpenAI


# =========================
# PAGE CONFIGURATION
# =========================

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide"
)


# =========================
# GROQ AI CONNECTION
# =========================

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)


# =========================
# AI FUNCTION
# =========================

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
        return f"AI connection failed\n\n{type(e).__name__}: {e}"


# =========================
# SESSION STATE
# =========================

if "page" not in st.session_state:
    st.session_state.page = "Home"


# =========================
# HOME PAGE
# =========================

if st.session_state.page == "Home":

    st.title("📚 StudySync")
    st.subheader("Your AI Powered Study Companion")

    st.write(
        "StudySync helps college students study smarter using "
        "AI Notes, Study Assistant, Quizzes and Flashcards."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Study Material", use_container_width=True):
            st.session_state.page = "Study Material"
            st.rerun()

    with col2:
        if st.button("🤖 AI Study Assistant", use_container_width=True):
            st.session_state.page = "AI Study Assistant"
            st.rerun()

    with col3:
        if st.button("📝 AI Notes Generator", use_container_width=True):
            st.session_state.page = "AI Notes Generator"
            st.rerun()

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("🎯 AI Quiz Generator", use_container_width=True):
            st.session_state.page = "AI Quiz Generator"
            st.rerun()

    with col5:
        if st.button("🃏 AI Flashcards", use_container_width=True):
            st.session_state.page = "Flashcards"
            st.rerun()

    with col6:
        if st.button("📊 Progress Tracker", use_container_width=True):
            st.session_state.page = "Progress Tracker"
            st.rerun()

    st.divider()

    st.success("🚀 StudySync AI is ready to help you study!")


# =========================
# STUDY MATERIAL
# =========================

elif st.session_state.page == "Study Material":

    st.title("📄 Study Material")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    st.write("Upload your PDF and generate AI-powered notes.")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        try:
            reader = PdfReader(uploaded_file)

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            st.success("PDF uploaded successfully!")

            st.subheader("📖 Extracted Text")

            st.text_area(
                "PDF Content",
                text[:5000],
                height=250
            )

            if st.button("✨ Generate AI Notes"):

                with st.spinner("Generating notes..."):

                    prompt = f"""
You are an AI study assistant.

Create simple and useful college-level notes from the following PDF content.

Use:
- Clear headings
- Bullet points
- Important definitions
- Important concepts
- Examples where useful
- Exam-friendly language

PDF CONTENT:

{text[:12000]}
"""

                    notes = ask_ai(prompt)

                st.subheader("📝 AI Generated Notes")
                st.write(notes)

        except Exception as e:
            st.error(f"PDF processing error: {e}")


# =========================
# AI STUDY ASSISTANT
# =========================

elif st.session_state.page == "AI Study Assistant":

    st.title("🤖 AI Study Assistant")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    st.write(
        "Ask anything related to your studies."
    )

    question = st.text_area(
        "Enter your question:",
        height=120
    )

    if st.button("Ask AI"):

        if question.strip() == "":
            st.warning("Please enter a question.")

        else:

            with st.spinner("AI is thinking..."):

                prompt = f"""
You are a helpful college study assistant.

Explain the answer in simple language so that a college student
can easily understand and revise it.

Use examples whenever useful.

Question:
{question}
"""

                answer = ask_ai(prompt)

            st.subheader("💡 AI Answer")
            st.write(answer)


# =========================
# AI NOTES GENERATOR
# =========================

elif st.session_state.page == "AI Notes Generator":

    st.title("📝 AI Notes Generator")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    topic = st.text_input(
        "Enter topic:",
        placeholder="Example: Artificial Intelligence"
    )

    if st.button("Generate Notes"):

        if topic.strip() == "":
            st.warning("Please enter a topic.")

        else:

            with st.spinner("Generating notes..."):

                prompt = f"""
Create easy-to-understand college notes on:

{topic}

Include:

1. Definition
2. Introduction
3. Important concepts
4. Key points
5. Real-life examples
6. Advantages
7. Disadvantages
8. Short conclusion

Use simple language and clear headings.
"""

                notes = ask_ai(prompt)

            st.subheader("📚 Generated Notes")
            st.write(notes)


# =========================
# AI QUIZ GENERATOR
# =========================

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

    if st.button("Generate Quiz"):

        if topic.strip() == "":
            st.warning("Please enter a topic.")

        else:

            with st.spinner("Generating quiz..."):

                prompt = f"""
Create exactly {number_of_questions} multiple-choice questions
for college students on:

{topic}

Use exactly this format for every question:

QUESTION: question text
A: option A
B: option B
C: option C
D: option D
ANSWER: A

The ANSWER must contain only A, B, C or D.

Make questions clear and educational.
"""

                quiz_text = ask_ai(prompt)

            # Parse questions
            lines = quiz_text.splitlines()

            questions = []
            current = {}

            for line in lines:

                line = line.strip()

                if line.startswith("QUESTION:"):
                    if current.get("question"):
                        questions.append(current)

                    current = {
                        "question": line.replace(
                            "QUESTION:", ""
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
                    current["answer"] = line.replace(
                        "ANSWER:", ""
                    ).strip().upper()

            if current.get("question"):
                questions.append(current)

            # Keep only complete questions
            valid_questions = []

            for q in questions:

                if (
                    q.get("question")
                    and q.get("A")
                    and q.get("B")
                    and q.get("C")
                    and q.get("D")
                    and q.get("answer") in ["A", "B", "C", "D"]
                ):
                    valid_questions.append(q)

            # Retry if AI generated fewer questions
            attempts = 0

            while (
                len(valid_questions) < number_of_questions
                and attempts < 3
            ):

                attempts += 1

                missing = number_of_questions - len(valid_questions)

                retry_prompt = f"""
Create exactly {missing} additional multiple-choice questions
on the topic:

{topic}

Do NOT repeat common questions.

Use exactly this format:

QUESTION: question text
A: option A
B: option B
C: option C
D: option D
ANSWER: A

ANSWER must be only A, B, C or D.
"""

                retry_text = ask_ai(retry_prompt)

                retry_lines = retry_text.splitlines()

                current = {}

                for line in retry_lines:

                    line = line.strip()

                    if line.startswith("QUESTION:"):

                        if current.get("question"):
                            questions.append(current)

                        current = {
                            "question": line.replace(
                                "QUESTION:", ""
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
                        current["answer"] = line.replace(
                            "ANSWER:", ""
                        ).strip().upper()

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

            valid_questions = valid_questions[
                :number_of_questions
            ]

            if not valid_questions:

                st.error(
                    "AI could not generate a valid quiz. Please try again."
                )

            else:

                st.success(
                    f"Generated {len(valid_questions)} questions."
                )

                user_answers = {}

                for i, q in enumerate(valid_questions):

                    st.markdown(
                        f"### Question {i + 1}"
                    )

                    st.write(q["question"])

                    user_answers[i] = st.radio(
                        "Choose your answer:",
                        [
                            q["A"],
                            q["B"],
                            q["C"],
                            q["D"]
                        ],
                        key=f"quiz_{i}"
                    )

                if st.button("✅ Submit Quiz"):

                    score = 0

                    answer_letters = {
                        q["A"]: "A",
                        q["B"]: "B",
                        q["C"]: "C",
                        q["D"]: "D"
                    }

                    for i, q in enumerate(valid_questions):

                        selected = user_answers[i]

                        selected_letter = answer_letters.get(
                            selected
                        )

                        if selected_letter == q["answer"]:
                            score += 1

                    total = len(valid_questions)

                    percentage = (
                        score / total
                    ) * 100

                    st.divider()

                    st.subheader("🏆 Quiz Result")

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

                    st.subheader("📋 Answer Review")

                    for i, q in enumerate(valid_questions):

                        selected = user_answers[i]

                        correct_option = q[
                            q["answer"]
                        ]

                        if selected == correct_option:

                            st.success(
                                f"Question {i + 1}: Correct ✅"
                            )

                        else:

                            st.error(
                                f"Question {i + 1}: "
                                f"Correct answer: {correct_option}"
                            )


# =========================
# FLASHCARDS
# =========================

elif st.session_state.page == "Flashcards":

    st.title("🃏 AI Flashcards")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    topic = st.text_input(
        "Enter topic:",
        placeholder="Example: Python Programming"
    )

    if st.button("Generate Flashcards"):

        if topic.strip() == "":
            st.warning("Please enter a topic.")

        else:

            with st.spinner("Generating flashcards..."):

                prompt = f"""
Create 10 useful flashcards for college students
on the topic:

{topic}

Format:

Flashcard 1
Question:
Answer:

Flashcard 2
Question:
Answer:

Continue until Flashcard 10.

Keep answers short, simple and easy to revise.
"""

                cards = ask_ai(prompt)

            st.subheader("🃏 Flashcards")
            st.write(cards)


# =========================
# PROGRESS TRACKER
# =========================

elif st.session_state.page == "Progress Tracker":

    st.title("📊 Progress Tracker")

    if st.button("⬅️ Back"):
        st.session_state.page = "Home"
        st.rerun()

    st.write(
        "Track your study progress."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Study Progress",
            "65%"
        )

        st.metric(
            "Topics Completed",
            "13"
        )

    with col2:

        st.metric(
            "Quizzes Completed",
            "8"
        )

        st.metric(
            "Current Streak",
            "5 Days"
        )

    st.progress(0.65)

    st.success(
        "Keep studying consistently! 🚀"
    )
