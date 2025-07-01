import streamlit as st
import os
import re
import PyPDF2 as pdf
import docx2txt
import json
import plotly.graph_objects as go
import base64
import time
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# ─── ENVIRONMENT & NVIDIA LLM CONFIG ─────────────────────────────
load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY", "")

if not API_KEY.startswith("nvapi-"):
    raise RuntimeError("Missing or invalid NVIDIA_API_KEY")

llm = ChatNVIDIA(
    model="meta/llama-3.2-3b-instruct",
    temperature=0.4,
    top_p=0.7,
    api_key=API_KEY
)

# ─── STYLING ─────────────────────────────────────────────────────
st.set_page_config(page_title="HUBNEX LABS - Advanced Resume Evaluator", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
body, .stApp {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(to bottom, #f5f7fa, #c3cfe2);
    margin: 0;
}
h1 {
    font-weight: 600;
    text-align: center;
    color: #FFB800;
}
.stButton > button {
    width: 250px;
    height: 70px;
    background-color: #5F9EA0;
    color: white;
    font-size: 16px;
    border-radius: 8px;
}
.stButton > button:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)

# ─── BACKGROUND IMAGE ────────────────────────────────────────────
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded_image = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpg;base64,{encoded_image});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True
    )

add_bg_from_local('Background.jpg')  # Add your background image here

# ─── TEXT EXTRACTION FUNCTIONS ───────────────────────────────────
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    return "".join([page.extract_text() for page in reader.pages])

def input_docx_text(uploaded_file):
    return docx2txt.process(uploaded_file)

def input_txt_text(uploaded_file):
    return uploaded_file.read().decode("utf-8")

# ─── NVIDIA LLM PROMPT HANDLING ─────────────────────────────────
input_prompt = """
You are an experienced Application Tracking System (ATS) with expertise in evaluating resumes.
Your task is to assess the candidate's suitability for the role based on the provided job description.

Evaluate:
- Relevant skills
- Professional experience
- Education
- Certifications
- Industry tools
- Soft skills

resume: {text}
job_description: {job_description}

Return as JSON:
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""

def get_nvidia_response(prompt):
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return json.dumps({"JD Match": "0%", "MissingKeywords": [], "Profile Summary": f"Error: {str(e)}"})

def clean_response(response):
    try:
        cleaned_response = re.sub(r'[\x00-\x1F\x7F]', '', response)
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        return None

# ─── UI LAYOUT ──────────────────────────────────────────────────
st.markdown("<h1>📄 Resume Application Tracking System</h1>", unsafe_allow_html=True)
st.markdown("Upload your resume and compare it to a job description using NVIDIA LLM.")

job_description = st.text_area("📋 Paste the Job Description:", placeholder="Paste the job description here", height=150)
uploaded_file = st.file_uploader("📂 Upload Your Resume", type=["pdf", "docx", "txt"])
submit = st.button("Evaluate Resume")

def show_progress_bar():
    with st.spinner('Processing...'):
        time.sleep(5)

# ─── MAIN EVALUATION LOGIC ──────────────────────────────────────
if submit:
    if not job_description.strip():
        st.error("Please provide a job description.")
    elif uploaded_file:
        show_progress_bar()
        try:
            if uploaded_file.type == "application/pdf":
                resume_text = input_pdf_text(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = input_docx_text(uploaded_file)
            elif uploaded_file.type == "text/plain":
                resume_text = input_txt_text(uploaded_file)
            else:
                raise ValueError("Unsupported file format.")

            if not resume_text.strip():
                raise ValueError("Empty resume. Please upload a valid file.")

            filled_prompt = input_prompt.format(text=resume_text, job_description=job_description)
            response = get_nvidia_response(filled_prompt)
            response_json = clean_response(response)

            if response_json:
                percentage_match = int(response_json.get("JD Match", "0").strip('%'))

                with st.expander("Show Evaluation Results"):
                    st.subheader("🔍 Response JSON")
                    st.write(response_json)

                    def render_pie_chart(percentage):
                        fig = go.Figure(
                            data=[go.Pie(
                                labels=['Match', 'Gap'],
                                values=[percentage, 100 - percentage],
                                hole=0.5,
                                marker=dict(colors=['#4CAF50', '#F44336']),
                                textinfo='none',
                                hoverinfo='label+percent'
                            )]
                        )
                        fig.add_annotation(
                            x=0, y=0, text=f"<b>{percentage}%</b>", showarrow=False,
                            font=dict(size=40, color="#000000" if percentage >= 50 else "#FF0000")
                        )
                        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
                        return fig

                    st.subheader("📊 JD Match Score")
                    st.plotly_chart(render_pie_chart(percentage_match), use_container_width=True)

                    st.subheader("🔑 Missing Keywords")
                    st.write(response_json.get("MissingKeywords", []))

                    st.subheader("📝 Profile Summary")
                    st.write(response_json.get("Profile Summary", ""))

                    st.subheader("🔧 Skills Match Analysis")
                    st.write(get_nvidia_response(f"Compare resume to JD.\n\nresume: {resume_text}\njob_description: {job_description}"))

                    st.subheader("✍️ Grammar Check")
                    st.write(get_nvidia_response(f"Check resume grammar and formatting.\n\n{resume_text}"))

                    st.subheader("🔊 Tone & Language")
                    st.write(get_nvidia_response(f"Evaluate tone and professionalism.\n\n{resume_text}"))

                st.success("✅ Resume evaluated successfully!")
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
    else:
        st.warning("Please upload your resume.")

# ─── FOOTER ─────────────────────────────────────────────────────
footer = """
<style>
.footer {
    position: fixed;
    left: 0; bottom: 0;
    width: 100%;
    background-color: #4CAF50;
    color: white; text-align: center;
    padding: 10px 0;
}
.footer a {
    color: #FFFFFF;
    text-decoration: none;
    font-weight: bold;
}
.footer a:hover {
    color: #DFF6DD;
    text-decoration: underline;
}
</style>
<div class="footer">
    <p>Powered by <a href="https://www.hubnex.in/" target="_blank">HUBNEX LABS</a> |
    <a href="https://www.linkedin.com/in/vishwajit-singh-69175319b" target="_blank">LinkedIn</a> |
    <a href="https://github.com/VishuS1304" target="_blank">GitHub</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
