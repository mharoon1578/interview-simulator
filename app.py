import streamlit as st
from PyPDF2 import PdfReader
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent
from langchain_groq import ChatGroq
import os

def extract_text(file):
    try:
        reader = PdfReader(file)
        return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
    except Exception as e:
        return f"Error extracting text: {e}"

class InterviewSession:
    def __init__(self, groq_key, resume_text, job_role):
        self.job_role = job_role
        self.question_count = 0
        self.max_questions = 7
        self.transcript = []
        self.finished = False

        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        self.llm = ChatGroq(
            temperature=0.3,
            groq_api_key=groq_key,
            model_name="mistral-saba-24b"
        )

       self.base_prompt = f"""
You are a strict, professional hiring officer conducting a structured mock interview.

Your job:
- You are interviewing the user (the candidate) for the role of: {job_role}
- The user is NOT the interviewer. Do NOT ask what they want to discuss.
- You must behave as a senior recruiter assessing them for the job.

Here is the candidate's resume:

--- RESUME START ---
{resume_text}
--- RESUME END ---

Instructions:
- Ask exactly ONE interview question at a time.
- Start now with the FIRST question.
- Ask a total of SEVEN (7) questions.
- Wait for the user's answer before asking the next.
- Ask a mix of role-specific, technical, and behavioral questions.
- DO NOT explain yourself. DO NOT ask how you can help.
- After all 7 answers, give a FINAL EVALUATION that includes:
  - A score out of 100
  - Strengths
  - Areas to improve
  - Final decision (Pass or Fail)

Begin the mock interview now by asking your first question.
"""


        self.agent = initialize_agent(
            tools=[],
            llm=self.llm,
            agent="chat-conversational-react-description",
            verbose=False,
            memory=self.memory,
            system_message=self.base_prompt
        )

    def ask_next(self, user_input=None):
        if self.finished:
            return "The interview is already complete."

        if user_input:
            self.transcript.append(("You", user_input))
            self.question_count += 1

        if self.question_count < self.max_questions:
            if user_input:
                prompt = user_input
            else:
                prompt = f"You are the interviewer. Ask question {self.question_count + 1} now."
            question = self.agent.run(prompt)
            self.transcript.append(("AI", question))
            return question

        else:
            self.finished = True
            full_convo = "\n".join([f"{s}: {m}" for s, m in self.transcript])
            eval_prompt = f"""
This is a 7-question mock interview for a {self.job_role} role.  
Transcript:
{full_convo}

Provide a structured evaluation:
1. Final Score (out of 100)
2. Strengths shown
3. Areas for improvement
4. Final Verdict (Pass or Fail) with reason
"""
            result = self.agent.run(eval_prompt)
            self.transcript.append(("AI", result))
            return result

st.title("AI-Powered Interview Simulation")

st.subheader("Interview Chatbot")

if "step" not in st.session_state:
    st.session_state.step = "ask_api"
    st.session_state.chat_history = []

# Step 1: Ask for Groq API key
if st.session_state.step == "ask_api":
    st.chat_message("assistant").markdown("Please enter your Groq API key to begin:")
    api_input = st.text_input("Enter your Groq API Key", type="password")
    if api_input:
        st.session_state.groq_key = api_input
        st.session_state.step = "ask_resume"
        st.rerun()

# Step 2: Upload resume
elif st.session_state.step == "ask_resume":
    st.chat_message("assistant").markdown("Please upload your resume PDF:")
    uploaded_file = st.file_uploader("Upload Resume", type="pdf")
    if uploaded_file:
        text = extract_text(uploaded_file)
        if text.startswith("Error"):
            st.error(text)
        else:
            st.session_state.resume_text = text
            st.session_state.step = "confirm_start"
            st.rerun()

# Step 3: Confirm interview
elif st.session_state.step == "confirm_start":
    st.chat_message("assistant").markdown("Resume received. What job role are you interviewing for?")
    job_input = st.chat_input("e.g., Data Scientist, Product Manager")
    if job_input:
        st.session_state.job_role = job_input
        st.session_state.step = "start_interview"
        st.session_state.chat_history.append(("You", job_input))
        st.session_state.session = InterviewSession(
            st.session_state.groq_key,
            st.session_state.resume_text,
            job_input
        )
        with st.spinner("Thinking..."):
            response = st.session_state.session.ask_next()
        st.session_state.chat_history.append(("AI", response))
        st.rerun()

# Step 4: Interview logic
elif st.session_state.step == "start_interview":
    if "session" not in st.session_state:
        st.session_state.session = InterviewSession(
            st.session_state.groq_key,
            st.session_state.resume_text,
            st.session_state.job_role
        )
    if not st.session_state.session.finished:
        for sender, msg in st.session_state.chat_history:
            st.chat_message("user" if sender == "You" else "assistant").markdown(msg)

        user_input = st.chat_input("Your answer...")
        if user_input:
            st.session_state.chat_history.append(("You", user_input))
            with st.spinner("Thinking..."):
                response = st.session_state.session.ask_next(user_input)
            st.session_state.chat_history.append(("AI", response))
            st.rerun()
    else:
        st.success("Interview complete. See final evaluation above.")
        if st.button("Restart Interview"):
            st.session_state.clear()
            st.rerun()
