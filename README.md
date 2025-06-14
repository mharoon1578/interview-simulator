# AI Interview Simulator Chatbot

An AI-powered mock interview chatbot built with LangChain, Groq API, and Streamlit. Upload your resume, choose a job role, and experience a 7-question AI-conducted mock interview — complete with feedback, scoring, and a final verdict.

---

## Features

*  Secure Groq API key entry (password-masked)
*  Resume PDF parsing and analysis
*  Job role-based interview customization
*  AI acts as a strict hiring officer
*  Structured 7-question interview (behavioral + technical)
*  Final evaluation including:

  * Score (0–100)
  * Strengths
  * Areas for improvement
  * Pass/Fail verdict
*  Streamlit chat UI with memory
*  Restart interview anytime

---

## Tech Stack

* **LangChain** – agent and prompt orchestration
* **Groq API** – blazing-fast LLM (e.g., `mistral-saba-24b`)
* **Streamlit** – UI and user interaction
* **PyPDF2** – PDF resume parsing

---

## Installation

```bash
git clone https://github.com/mharoon1578/interview-simulator
cd interview-simulator
pip install -r requirements.txt
```

---

## Run the App

```bash
streamlit run app.py
```

You will be prompted to enter your Groq API key and upload your resume.

---

## Usage Flow

1. Enter your **Groq API key** (secure)
2. Upload your **resume PDF**
3. Enter your **target job role** (e.g., "AI Engineer")
4. AI will:

   * Ask 7 tailored questions
   * Respond to your answers
   * Generate a final structured evaluation

---

## Project Structure

```bash
interview-simulator/
├── app.py             # Streamlit UI and logic
├── README.md          # Documentation
├── requirements.txt   # Dependencies
```

---
