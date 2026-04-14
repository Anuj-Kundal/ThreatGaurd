from flask import Flask, render_template, request
from google import genai
import os
import PyPDF2

# Initialize Flask app
app = Flask(__name__)

# Set up the Google API Key

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# functions
def predict_fake_or_real_email_content(text):
    prompt = f"""
You are an expert in identifying scam messages.

Classify the following email into one category:
- Scam/Fake
- Real/Legitimate

ONLY return the classification message.

Email content:
{text}
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return response.text.strip()



def url_detection(url):
    prompt = f"""
Analyze the following URL and determine if it is malicious or safe.

Only return:
- Malicious URL
- Safe URL

URL:
{url}
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return response.text.strip()



# Routes

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/scam/', methods=['POST'])
def detect_scam():
    if 'file' not in request.files:
        return render_template("index.html", message="No file uploaded.")

    file = request.files['file']
    extracted_text = ""

    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif file.filename.endswith('.txt'):
        extracted_text = file.read().decode("utf-8")
    else:
        return render_template("index.html", message="Invalid file type. Please upload a PDF or TXT file.")

    if not extracted_text.strip():
        return render_template("index.html", message="File is empty or text could not be extracted.")

    message = predict_fake_or_real_email_content(extracted_text)
    return render_template("index.html", message=message)


@app.route('/predict', methods=['POST'])
def predict_url():
    url = request.form.get('url', '').strip()

    if not url.startswith(("http://", "https://")):
        return render_template("index.html", message="Invalid URL format.", input_url=url)

    classification = url_detection(url)
    return render_template("index.html", input_url=url, predicted_class=classification)


if __name__ == '__main__':
    app.run(debug=True)
