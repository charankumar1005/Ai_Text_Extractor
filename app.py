from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF
import io
from docx import Document

app = Flask(__name__)
CORS(app)

genai.configure(api_key="AIzaSyBcioXsLMrauHr8t_39gR_Dkqo0pHIngsw")

def extract_text_from_pdf(file_stream):
    doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_stream):
    doc = Document(file_stream)
    return '\n'.join([para.text for para in doc.paragraphs])

@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = file.filename.lower()

    model = genai.GenerativeModel('gemini-1.5-flash')

    try:
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file.stream)
            response = model.generate_content(
                [image, "Extract all the important information from this document in a structured format."],
                stream=False
            )
        elif filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
            response = model.generate_content(
                [text, "Extract all the important information from this PDF in a structured format."],
                stream=False
            )
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
            response = model.generate_content(
                [text, "Extract all the important information from this Word document in a structured format."],
                stream=False
            )
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
            response = model.generate_content(
                [text, "Extract all the important information from this text file in a structured format."],
                stream=False
            )
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        return jsonify({'result': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
