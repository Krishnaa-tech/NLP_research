# import PyPDF2

# from datetime import datetime
import re 
import spacy
from transformers import AutoTokenizer, PegasusForConditionalGeneration

# Function to read PDF files and store the extracted text in a text file
# def read_pdf(file_path):
#     timestamp = datetime.now().strftime("Y%Y_M%m_D%dT_%H_%M_%S") 
#     cleaned_path = re.sub(r'[:.\/\\*\?"<>|]', '_', file_path)
#     new_text_file_name =  f"{cleaned_path}_output_{timestamp}.txt"
#     with open(file_path, 'rb') as pdf_file:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         text = ""
#         for page_num in range(len(pdf_reader.pages)):
#             page = pdf_reader.pages[page_num]
#             text += page.extract_text()

#         text_to_txt = clean_text(text)
#     try:
#         with open(new_text_file_name, 'w', encoding='utf-8') as file:
#             file.write(text_to_txt)
#         print(f"Text has been successfully written to {new_text_file_name}")
#         return new_text_file_name
#     except Exception as e:
#         print(f"Error while writing to the file: {e}")

        # Function to read text files and store the text in a variable
        
def read_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()
            text = clean_text(text)       
        return text
    except Exception as e:
        print(f"Error while processing the text file: {e}")
        return None
    

def clean_text(text):
    # Remove line breaks and extra spaces
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    # Remove unwanted characters
    text = re.sub(r'[^A-Za-z0-9.,?!()\'":;\-]', ' ', text)

    # Add missing spaces after punctuation marks
    text = re.sub(r'([.,?!();:])', r'\1 ', text)

    # Remove extra spaces after punctuation marks
    text = re.sub(r'\s+([.,?!();:])', r'\1', text)

    # Remove spaces before punctuation marks
    text = re.sub(r'\s([.,?!();:])', r'\1', text)

    # Remove spaces before and after hyphens
    text = re.sub(r'\s-\s', '-', text)
    text = re.sub(r'\s-', '-', text)
    text = re.sub(r'-\s', '-', text)

    # Trim leading and trailing spaces
    text = text.strip()

    return text

def extract_proper_noun_phrases(text):
    # Load the spaCy English language model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    # Process the text using spaCy
    doc = nlp(text)

    # Extract proper noun phrases
    proper_noun_phrases = [
        " ".join([token.text for token in phrase])
        for phrase in doc.noun_chunks
        if any(token.pos_ == 'PROPN' for token in phrase)
    ]
    return proper_noun_phrases


def generate_summary(article_text):
    # Load pre-trained model and tokenizer
    model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-xsum")
    tokenizer = AutoTokenizer.from_pretrained("google/pegasus-xsum")

    # Tokenize the input text
    inputs = tokenizer(article_text, max_length=1024, return_tensors="pt")

    # Generate Summary
    summary_ids = model.generate(inputs["input_ids"])

    # Decode and return the summary
    summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    return summary