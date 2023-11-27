from django.shortcuts import render
from . import utils
# from .models import Article
from transformers import AutoTokenizer, PegasusForConditionalGeneration
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import google.generativeai as genai
import os
from decouple import config


# Create your views here:
def home(request): 
    return render(request,'main/index.html')

# Function to identify and process the uploaded file
def process_uploaded_file(uploaded_file_path):
    # if uploaded_file_path.endswith('.pdf'):
    #     # It's a PDF, read and store the text in a text file
    #     file_name = utils.read_pdf(uploaded_file_path)
    #     with open(file_name, 'r', encoding='utf-8') as txt_file:
    #         text = txt_file.readlines()
    #     return text

    if uploaded_file_path.endswith('.txt'):
        # It's a text file, read the text directly into a variable
        return utils.read_text(uploaded_file_path)
    else:
        print("Unsupported file format. Please upload a PDF or a text file.")
        return None
  
# def document(request):
#     if request.method == 'POST' and request.FILES['uploaded_file']:
#         uploaded_file = request.FILES['uploaded_file']
#         file_path = process_uploaded_file(uploaded_file)

#         if file_path:
#             text_content = process_uploaded_file(file_path)
#             return render(request, 'ner.html', {'text_content': text_content})
#         else:
#             error_message = "Unsupported file format. Please upload a PDF or a text file."
#             return render(request, 'ner.html', {'error_message': error_message})
#     else:
#         return render(request, 'main/ner.html')    
    
def document(request):
    if request.method == 'POST' and request.FILES['uploaded_file']:
        uploaded_file = request.FILES['uploaded_file']
        file_path = process_uploaded_file(uploaded_file)

        if file_path:
            text_content = process_uploaded_file(file_path)
            return render(request, 'ner.html', {'text_content': text_content})
        else:
            error_message = "Unsupported file format. Please upload a PDF or a text file."
            return render(request, 'ner.html', {'error_message': error_message})
    else:
        return render(request, 'main/ner.html')

    
def ner(request): 
    return render(request, 'main/ner.html')


def underline_words(request):
    input_text = ''
    output_text = ''

    if request.method == 'POST':
        input_text = request.POST.get('input_text', '')

        # Extract proper noun phrases
        words_to_underline_list = utils.extract_proper_noun_phrases(input_text)

        # Underline specified words in the text
        for word in words_to_underline_list:
            input_text = input_text.replace(word, f'<u>{word}</u>')

        output_text = input_text  # You can modify this based on additional processing

    return render(request, 'main/ner.html', {'input_text': input_text, 'output_text': output_text})


# def generate_summary(article_text):
#     # Load pre-trained model and tokenizer
#     model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-xsum")
#     tokenizer = AutoTokenizer.from_pretrained("google/pegasus-xsum")

#     # Tokenize the input text
#     inputs = tokenizer(article_text, max_length=1024, return_tensors="pt")

#     # Generate Summary
#     summary_ids = model.generate(inputs["input_ids"])

#     # Decode and return the summary
#     summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
#     return summary

# def summarize_article(request, article_id):
#     # Retrieve the article from the database
#     article = Article.objects.get(pk=article_id)

#     # Generate the summary using the function
#     summary = generate_summary(article.content)

#     # Pass the summary to the template
#     context = {'article': article, 'summary': summary}
#     return render(request, 'ner.html', context)



# load_dotenv()

# # Use the API key from the environment variable
# API_KEY = os.getenv("API_KEY", "your_default_api_key")
# genai.configure(api_key=API_KEY)

# genai.configure(api_key="AIzaSyBeKXOpP1-_Uuxl8BseTdR19uvlAnIbGlo")


# Load the API key from environment variable
# genai.configure(api_key=config('API_KEY', default=''))
genai.configure(api_key="AIzaSyBeKXOpP1-_Uuxl8BseTdR19uvlAnIbGlo")

def generate_summary(request):
    text_input = request.POST.get('text_input', '')
    # print(f"Received text_input: {text_input}")

    defaults = {
        'model': 'models/text-bison-001',
        'temperature': 0.9,
        'candidate_count': 1,
        'top_k': 40,
        'top_p': 0.95,
        'max_output_tokens': 1024,
        'stop_sequences': [],
        'safety_settings': [
            {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 1},
            {"category": "HARM_CATEGORY_TOXICITY", "threshold": 1},
            {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 2},
            {"category": "HARM_CATEGORY_SEXUAL", "threshold": 2},
            {"category": "HARM_CATEGORY_MEDICAL", "threshold": 2},
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 2},
        ],
    }

    prompt = f"""Summarize this paragraph and detail some relevant context.

    Text: "{text_input}"""

    # Define response after the genai.generate_text call
    response = genai.generate_text(
        **defaults,
        prompt=prompt
    )

    summary = response.result

    content = {'summary': summary}
    # print(f"Received text_input: {text_input}")
    # print(f"Generated summary: {summary}")

    return render(request, 'summary.html', content)


