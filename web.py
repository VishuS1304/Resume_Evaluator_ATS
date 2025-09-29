import streamlit as st
import google.generativeai as genai
import os
import re
import PyPDF2 as pdf
from docx import Document
from dotenv import load_dotenv
import json
import plotly.graph_objects as go
import base64
import time
from datetime import datetime

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# UI Styling
st.set_page_config(page_title="HUBNEX LABS - Advanced Resume Evaluator", page_icon="💼", layout= "wide",initial_sidebar_state="expanded")
st.markdown("""
<style>
/* Global styling */
    body, .stApp {
        font-family: 'Arial', sans-serif;
        color: #FFFFFF;
        background-color: #2E3B4E;
        background: linear-gradient(to bottom, #f5f7fa, #c3cfe2);
        margin: 0;

    }
    h1 {
            font-weight: 600;
            margin-bottom: 10px;
            text-align: center;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            color: #FFB800;
    }
    .stButton > button {
        width: 250px;
        height: 70px;
        background-color: #5F9EA0;
        color: white;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
        border-radius: 8px;
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .stTextInput, .stFileUploader {
        background-color: #3A4E73;
        color: white;
        border-radius: 10px;
        border: 2px solid #4CAF50;
        padding: 10px;
    }
    .stTextInput:hover, .stFileUploader :hover {
        border-color: #45a049;
    }
    .stExpander {
        background-color: #2E3B4E;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Function to add a custom background image
def add_bg_from_local(image_file):
    """Add a background image to the Streamlit app."""
    with open(image_file, "rb") as image:
        encoded_image = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"jpg"};base64,{encoded_image});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
      
# Call the function with your image file
add_bg_from_local('Background.jpg')  # Use a high-quality background image

# Read the CSS file for additional styling
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to get current date in the desired format
def get_current_date():
    Date = datetime.now().strftime('%B %d, %Y')  # Example: "December 05, 2024"
    return Date

# Extract text from uploaded PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

# Extract text from uploaded DOCX file
def input_docx_text(uploaded_file):
    doc = Document(uploaded_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text
    
# Extract text from uploaded TXT file
def input_txt_text(uploaded_file):
    return uploaded_file.read().decode("utf-8")

# Get response from Gemini API
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

# Function to show progress while processing
def show_progress_bar():
    with st.spinner('Processing...'):
        time.sleep(5)  # Simulate processing delay

# Generalized Prompt Template for various job roles
input_prompt = """
You are an experienced Application Tracking System (ATS) with expertise in evaluating resumes
for a wide range of job roles across different industries. Your task is to assess the candidate's
suitability for the role based on the provided job description.

Please assign a percentage match based on how well the resume aligns with the job description
and highlight any missing keywords with high accuracy.

Key areas to evaluate:
- Relevant skills and competencies
- Professional experience and achievements
- Educational background and qualifications
- Certifications and training
- Knowledge of industry-specific tools and technologies
- Soft skills and personal attributes
- Alignment with the job responsibilities and requirements

resume: {text}
job_description: {job_description}

I want the response in a structured format:
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""
tenure_prompt = """Analyze the **Professional Work Experience** section of the resume, focusing exclusively on organizational-level roles (jobs held in formal organizations, excluding internships or non-organizational experiences).
For each organizational role, extract the following details:.
- **Duration of Employment**: Start and end dates, or the total duration in months/years. If a role is ongoing, calculate the duration up to today's date.
- **Gaps Between Roles**: Any periods of unemployment between consecutive organizational roles, with their durations.
Based on this data, provide:
1. **Average Tenure per Job**: Calculate the average time the employee spent in each organizational role.
2. **Career Timeline**: Summarize the total time spent in formal organizational roles, including any ongoing roles calculated up to today's date.
3. **Patterns and Insights**: Identify trends such as:
   - Consistency in tenure across roles.
   - Significant variations in job durations.
   - Gaps in employment and their potential implications.
Ensure the analysis is based only on the **Professional Work Experience** section of the resume. Ignore any unrelated sections or informal experiences.
Resume: {text}
"""

def clean_response(response):
    """Clean and parse the response from the Gemini API."""
    try:
        cleaned_response = re.sub(r'[\x00-\x1F\x7F]', '', response)
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        return None

# Streamlit app layout with a title and company name
st.markdown("<div class='title'> <span> HUBNEX LABS - Advanced Resume Evaluator </span> </div>", unsafe_allow_html=True)

st.markdown("<div class='subtitle'>How good is your resume? </div>", unsafe_allow_html=True)

st.markdown("<div class='subtitle'>Find out instantly. Upload your resume and our free resume scanner will evaluate it against key criteria hiring managers and applicant tracking systems (ATS) look for. Get actionable feedback on how to improve your resume's success rate.</div>", unsafe_allow_html=True)

# Title for Streamlit app
st.markdown("<h1>📄Resume Application Tracking System</h1>", unsafe_allow_html=True)
st.markdown("""
     <div style="text-align: center; color: #FFFFFF; font-size: 18px;">
        </div>""", unsafe_allow_html=True)

# Text area for job description input
job_description = st.text_area("📋 Paste the Job Description:", key="input",  placeholder="Paste the job description here", height=150, help="Paste the job description here to match with your resume.")

# File uploader for resume input
uploaded_file = st.file_uploader("📂Upload Your Resume", type=["pdf", "docx", "txt"],  help="Upload your resume in PDF, DOCX or TEXT format.")

# Submit button 
submit = st.button("Evaluate Resume", key="submit")

if submit:
    if not job_description.strip():
        st.error("Error: Please provide a job description before uploading your resume.")
    elif uploaded_file is not None:
        show_progress_bar()  # Show progress bar while processing starts
        try:
            if uploaded_file.type == "application/pdf":
                resume_text = input_pdf_text(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = input_docx_text(uploaded_file)
            elif uploaded_file.type == "text/plain":
                resume_text = input_txt_text(uploaded_file)
            else:
                raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
            
            if not resume_text.strip():
                raise ValueError("Theuploaded resume is empty. Please check your file and try again.")
            
            # Prepare and send the request to Gemini API
            input_prompt_filled = input_prompt.format(text=resume_text, job_description=job_description)
            response = get_gemini_response(input_prompt_filled)

            # Process the response
            response_json = clean_response(response)

            if response_json:
                percentage_match = int(response_json.get("JD Match", "0").strip('%'))
                
                # Display results
                with st.expander("Show Evaluation Results"):
                    st.markdown("""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <i style="font-size: 24px; margin-right: 10px; color: #4CAF50;">📋</i>
                            <h3 style="display: inline; margin: 0; color: #4CAF50;">Response:</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    

                    def render_pie_chart(percentage_match):
                        """Render an enhanced pie chart with modern styling."""
                        gap_percentage = 100 - percentage_match

                        fig = go.Figure(
                            data=[
                                go.Pie(
                                    labels=['Match', 'Gap'], 
                                    values=[percentage_match, gap_percentage],
                                    hole=0.5,  # Makes it a donut chart
                                    marker=dict(
                                        colors=['#4CAF50', '#F44336'],  # Match and gap colors
                                        line=dict(color='#FFFFFF', width=2),  # Border around segments
                                    ),
                                    textinfo='none',  # Hide text on the slices
                                    hoverinfo='label+percent',  # Show detailed hover info
                                    pull=[0.1, 0],  # Slightly "pull out" the Match section for emphasis
                                )
                            ]
                        )

                        fig.add_annotation(
                            x=0, y=0,
                            text=f"<b>{percentage_match}%</b>",
                            showarrow=False,
                            font=dict(
                                family="Arial",
                                size=40,
                                color="#000000" if percentage_match >= 50 else "#FF0000"
                            )
                        )

                        fig.update_layout(
                            showlegend=False,
                            margin=dict(t=20, b=20, l=20, r=20),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            height=400,
                        )

                        return fig
                    # Display Percentage Match with Chart
                    st.markdown("""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <i style="font-size: 24px; margin-right: 10px; color: #4CAF50;">📊</i>
                            <h3 style="display: inline; margin: 0; color: #4CAF50;">Percentage Match:</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    st.plotly_chart(render_pie_chart(percentage_match), use_container_width=True)
                    # Tenure analysis
                    st.markdown("""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <i style="font-size: 20px; margin-right: 10px; color: #4CAF50;">📅</i>
                            <h3 style="display: inline; margin: 0; color: #4CAF50;">Tenure Analysis</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    tenure_analysis_response = get_gemini_response(tenure_prompt.format(text=resume_text))
                    st.write(tenure_analysis_response)
                    
                    # Detailed analysis sections
                    st.markdown("""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <i style="font-size: 20px; margin-right: 10px; color: #4CAF50;">🔑</i>
                            <h3 style="display: inline; margin: 0; color: #4CAF50;">Missing Keywords</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    st.write(get_gemini_response(f"Identify keywords missing from the resume that are present in the job description.\n\nresume: {resume_text}\njob_description: {job_description}"))

                    st.markdown("""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <i style="font-size: 20px; margin-right: 10px; color: #4CAF50;">⚙️</i>
                            <h3 style="display: inline; margin: 0; color: #4CAF50;">Skills Match Analysis</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    st.write(get_gemini_response(f"Compare resume skills to the job description.\n\nresume: {resume_text}\njob_description: {job_description}"))

                    st.markdown("""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <i style="font-size: 20px; margin-right: 10px; color: #4CAF50;">📝</i>
                            <h3 style="display: inline; margin: 0; color: #4CAF50;">Profile Summary</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    st.write(get_gemini_response(f"Provide a Profile Summary and suggest improvements.\n\nresume: {resume_text}\njob_description: {job_description}"))

                    st.markdown("""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <i style="font-size: 20px; margin-right: 10px; color: #4CAF50;">✍️</i>
                            <h3 style="display: inline; margin: 0; color: #4CAF50;">Grammar and Formatting Check</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    st.write(get_gemini_response(f"Review the grammar and formatting of the resume.\n\nresume: {resume_text}\njob_description: {job_description}"))
                    
                    st.markdown("""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <i style="font-size: 20px; margin-right: 10px; color: #4CAF50;">🔊</i>
                            <h3 style="display: inline; margin: 0; color: #4CAF50;">Tone and Language</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    st.write(get_gemini_response(f"Evaluate the tone and language of the resume for alignment with the job description.\n\nresume: {resume_text}\njob_description: {job_description}"))
                
                # Success message
                st.success("Resume successfully analyzed! 🎉")

        except Exception as e:
            st.error(f"Error: {str(e)}")   
    else:
        st.warning("Please upload a resume file.")
          
# Custom Footer with date and additional styling
footer = f"""
<style>
.footer {{
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #4CAF50;
    color: white;
    text-align: center;
    padding: 10px 0;
}}

.footer-left {{
    position: fixed;
    left: 10px;
    bottom: 10px;
    color: white;
    font-size: 14px;
}}

.footer a {{
    color: #FFFFFF;
    text-decoration: none;
    font-weight: bold;
    margin: 0 15px;
}}

.footer a:hover {{
    text-decoration: underline;
    color: #DFF6DD;
}}
</style>
<div class="footer">
    <p>Powered by <a href="https://www.hubnex.in/" target="_blank">HUBNEX LABS</a> | Follow us on 
    <a href="https://www.linkedin.com/in/vishwajit-singh-69175319b" target="_blank">LinkedIn</a> |
    <a href="https://github.com/VishuS1304" target="_blank">GitHub</a></p>
</div>
<div class="footer-left">
    <p>{get_current_date()}</p>  <!-- Display current date -->
</div>
"""

st.markdown(footer, unsafe_allow_html=True)
