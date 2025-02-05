# Resumetrics - Resume-Application-Tracking-System

## Overview
Resumetrics is an advanced Application Tracking System (ATS) tool powered by Google's Gemini API. It evaluates resumes for alignment with job descriptions, providing percentage matches, identifying missing keywords, and summarizing profiles effectively.

🚀 Live Demo: https://resumetrics.streamlit.app

## Features
- **Resume Parsing:** Upload resumes in PDF, DOCX, or TXT formats and extract the text content.
- **Job Description Input:** Paste the job description for the role you're hiring for.
- **Resume Matching:** The application uses the **Gemini API** to assess how well the resume matches the job description.
- **Percentage Match:** View a percentage match based on the alignment of the resume with the job description.
- **Missing Keywords:** Get a list of missing keywords that the candidate's resume does not include but are important for the job.
- **Profile Summary:** Receive a brief summary of the candidate's profile, highlighting strengths and areas of improvement.
- **Visual Representation:** Display a pie chart visualizing the percentage match between the job description and the resume.

## Requirements
To run the application, you need to install the following dependencies:

- Python 3.7+
- Streamlit
- Google Gemini API
- PyPDF2
- python-docx
- python-dotenv
- Plotly
- Pandas

You can install the dependencies using the following command:

```bash
pip install -r requirements.txt
```
## Setup Instructions
#### 1. Clone this repository:
```bash
git clone https://github.com/your-username/resume-application-tracking-system.git
cd resume-application-tracking-system
```

#### 2. Create a .env file in the project root directory and add your Google API key:
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

#### 3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

#### 4. Run the Streamlit app:
```bash
streamlit run app.py
```

## How to Use
1. **Input the Job Description:** Paste the job description for the role you want to evaluate resumes against.
2. **Upload the Resume:** Upload the candidate's resume in PDF, DOCX, or TXT format.
3. **Submit the Resume:** Click the "Submit" button to get a detailed match report.
4. **Review the Results:** The app will display the percentage match, missing keywords, and a profile summary. A pie chart will visualize the percentage match.

## Example
1. Paste the job description for a Data Scientist role.
2. Upload a resume.
3. The system will show the match percentage, missing keywords like "Python," "Machine Learning," and "Data Analysis," and the candidate's profile summary.
   
## Technologies Used
- **Streamlit** for creating the interactive web interface.
- **Google Gemini API** for generating insights and evaluating resumes.
- **PyPDF2** for parsing text from PDF resumes.
- **python-docx** for parsing text from DOCX resumes.
- **Plotly** for visualizing the match percentage in pie charts.
- **pandas** for data handling and manipulation.
- **python-dotenv** for managing environment variables.

## Contributing
Feel free to contribute to this project by forking the repository and submitting a pull request with improvements or bug fixes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
Thanks to the **Google Gemini API** for providing powerful content generation capabilities.
Thanks to **Streamlit** for making it easy to create interactive web apps in Python.
