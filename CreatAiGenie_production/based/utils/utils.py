import os
import logging
from typing import Optional
import fitz  # PyMuPDF
import pandas as pd
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up OpenAI client
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

def summarize_text(text, model="gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

def generate_image_from_text(prompt: str) -> Optional[str]:
    try:
        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"An error occurred during image generation: {e}")
        return None

def extract_text_from_file(file) -> Optional[str]:
    try:
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension == '.pdf':
            return extract_text_from_pdf(file)
        elif file_extension == '.csv':
            return extract_text_from_csv(file)
        elif file_extension == '.docx':
            return extract_text_from_docx(file)
        elif file_extension == '.txt':
            return extract_text_from_txt(file)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return None
    except Exception as e:
        logger.error(f"An error occurred during text extraction: {e}")
        return None

def extract_text_from_pdf(file) -> str:
    doc = fitz.open(stream=file.read(), filetype='pdf')
    return " ".join(page.get_text() for page in doc)

def extract_text_from_csv(file) -> str:
    df = pd.read_csv(file)
    return df.to_string()

def extract_text_from_docx(file) -> str:
    doc = Document(file)
    return "\n".join(para.text for para in doc.paragraphs)

def extract_text_from_txt(file) -> str:
    return file.read().decode('utf-8')
