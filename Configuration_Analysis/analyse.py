import os
import zipfile
import tempfile
import logging
import requests
from flask import Flask, request, send_file, render_template_string
from pathlib import Path
from fpdf import FPDF

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Replace with your actual GROQ API Key
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"

# Path to Downloads folder
DOWNLOADS_PATH = str(Path.home() / "Downloads")

# HTML template for upload page
UPLOAD_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Android Project Analyzer</title>
  <style>
    body {
      background: #f9f9f9;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 0;
    }
    .container {
      max-width: 600px;
      margin: 80px auto;
      background: #ffffff;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
      text-align: center;
    }
    h2 {
      margin-bottom: 30px;
      color: #333;
    }
    input[type="file"] {
      display: block;
      margin: 20px auto;
      border: 2px dashed #ccc;
      padding: 15px;
      width: 100%;
      max-width: 400px;
      font-size: 16px;
      cursor: pointer;
      border-radius: 8px;
      background-color: #fafafa;
      transition: border 0.3s ease;
    }
    input[type="file"]:hover {
      border-color: #00aaff;
    }
    input[type="submit"] {
      background-color: #007bff;
      color: white;
      border: none;
      padding: 12px 25px;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
      margin-top: 20px;
      transition: background-color 0.3s ease;
    }
    input[type="submit"]:hover {
      background-color: #0056b3;
    }
    footer {
      text-align: center;
      margin-top: 60px;
      color: #aaa;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Upload Your Android Project (.zip)</h2>
    <form method="post" enctype="multipart/form-data" action="/analyze">
      <input type="file" name="file" required>
      <input type="submit" value="Analyze Project">
    </form>
  </div>
</body>
</html>
'''



# Util: Read important project files
def read_file_contents(base_path, file_names=["AndroidManifest.xml", "build.gradle", "proguard-rules.pro"]):
    contents = {}
    for file_name in file_names:
        file_path = find_file(base_path, file_name)
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    contents[file_name] = f.read()
            except Exception as e:
                contents[file_name] = f"Error reading {file_name}: {str(e)}"
        else:
            contents[file_name] = f"{file_name} not found"
    return contents


# Util: Use GROQ API to analyze
def get_vulnerability_analysis(file_contents):
    prompt = f"""
You are an expert Android security analyst. Based on the following configuration files from an Android project, provide a detailed analysis of potential security and privacy vulnerabilities, SDK compatibility issues, insecure permissions, or misconfigurations.

Files:
{file_contents}

Give actionable recommendations and organize the response by file.
"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are an Android security expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error from GROQ API: {response.status_code} - {response.text}"


# Util: Generate PDF from GROQ response
def generate_pdf_report_from_groq(groq_response, report_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, txt="Android Project Vulnerability Report", align="C")
    pdf.ln(5)

    pdf.set_font("Arial", size=10)
    for line in groq_response.split("\n"):
        pdf.multi_cell(0, 8, txt=line)

    report_path = os.path.join(DOWNLOADS_PATH, report_name)
    pdf.output(report_path)
    return report_path


# Util: Search file in directory
def find_file(base_path, file_name):
    for root, dirs, files in os.walk(base_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None


# Util: Print directory structure
def print_dir_structure(path):
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")


# Route: Upload UI
@app.route('/')
def upload_file():
    return render_template_string(UPLOAD_HTML)


# Route: Analyze uploaded project
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return "No file uploaded", 400

    zip_file = request.files['file']
    if zip_file.filename == '':
        return "No selected file", 400

    temp_zip_path = os.path.join(tempfile.gettempdir(), zip_file.filename)
    zip_file.save(temp_zip_path)

    try:
        with tempfile.TemporaryDirectory() as extract_path:
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            logging.debug("Extracted file structure:")
            print_dir_structure(extract_path)

            # Read contents of key config files
            files_to_analyze = read_file_contents(extract_path)

            # Combine into single string for GROQ
            file_combined_str = "\n\n".join(f"--- {fname} ---\n{content}" for fname, content in files_to_analyze.items())

            # Get vulnerability report
            groq_report = get_vulnerability_analysis(file_combined_str)

            # Generate PDF
            report_name = f"vulnerability_report_{zip_file.filename.replace('.zip','')}.pdf"
            report_path = generate_pdf_report_from_groq(groq_report, report_name)

            return send_file(report_path, as_attachment=True)

    finally:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)