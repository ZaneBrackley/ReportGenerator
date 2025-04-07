from flask import Flask, render_template, request
import PyPDF2

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = None

    if request.method == 'POST':
        # Handle the file upload
        uploaded_files = request.files.getlist('file')
        for file in uploaded_files:
            if file.filename.endswith('.pdf'):
                text = extract_text_from_pdf(file)
                extracted_text = text  # Extracted raw text from PDF
            else:
                extracted_text = "Please upload a valid PDF file."

    return render_template('index.html', text=extracted_text)


def extract_text_from_pdf(pdf_file):
    # Initialize PDF reader
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    
    # Extract text from each page
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text


if __name__ == "__main__":
    app.run(debug=True)
