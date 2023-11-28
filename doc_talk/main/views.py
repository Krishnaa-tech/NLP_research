from django.shortcuts import render
from . import utils
# from .utils import summarize_article
from transformers import AutoTokenizer, PegasusForConditionalGeneration
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import google.generativeai as genai
import os
from rouge_score import rouge_scorer
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render


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


# def underline_words(request):
#     input_text = ''
#     output_text = ''

#     if request.method == 'POST':
#         input_text = request.POST.get('input_text', '')

#         # Extract proper noun phrases
#         words_to_underline_list = utils.extract_proper_noun_phrases(input_text)

#         # Underline specified words in the text
#         for word in words_to_underline_list:
#             input_text = input_text.replace(word, f'<u>{word}</u>')

#         output_text = input_text  # You can modify this based on additional processing

#     return render(request, 'main/ner.html', {'input_text': input_text, 'output_text': output_text})



def get_wikipedia_suggestions(query):
    # Wikipedia API endpoint for search suggestions
    url = 'https://en.wikipedia.org/w/api.php'

    # Parameters for the API request
    params = {
        'action': 'opensearch',
        'format': 'json',
        'search': query,
        'limit': 5,  # Limit the number of suggestions
    }

    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the suggestions from the API response
    suggestions = data[1]
    return suggestions

def display_suggestions_with_numbers(suggestions):
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")

def get_wikipedia_article_by_keyword(keyword):
    # Wikipedia API endpoint for fetching page content
    url = 'https://en.wikipedia.org/w/api.php'

    # Parameters for the API request
    params = {
        'action': 'query',
        'format': 'json',
        'titles': keyword,
        'prop': 'extracts',
        'exintro': True,  # Get only the introductory section
    }

    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the page content
    pages = data.get('query', {}).get('pages', {})
    for page_id, page_info in pages.items():
        title = page_info.get('title', '')
        content = page_info.get('extract', '')

        # Check if content is not empty
        if content:
            # Use BeautifulSoup to clean up the HTML content
            soup = BeautifulSoup(content, 'html.parser')
            cleaned_content = soup.get_text()
            return {'title': title, 'content': cleaned_content.strip()}

    # If no content is found
    return {'title': f"No article found for '{keyword}'", 'content': "No content available."}

def get_wikipedia_content(keyword):
    article = get_wikipedia_article_by_keyword(keyword)
    return f"\nTitle: {article['title']}\nContent: {article['content']}"

def underline_words(request):
    input_text = ''
    output_text = ''
    word_reference = []

    if request.method == 'POST':
        input_text = request.POST.get('input_text', '')

        # Extract proper noun phrases
        words_to_underline_list = utils.extract_proper_noun_phrases(input_text)

        # Underline specified words in the text and fetch Wikipedia content
        for word in words_to_underline_list:
            input_text = input_text.replace(word, f'<u data-toggle="tooltip" title="Loading summary..." class="underlined" data-word="{word}">{word}</u>')

            # Get Wikipedia content for each underlined word
            article = get_wikipedia_article_by_keyword(word)
            word_reference.append({'word': word, 'content': article['content']})

        output_text = input_text

    return render(request, 'main/ner.html', {'input_text': input_text, 'output_text': output_text, 'word_reference': word_reference})

def calculate_rouge(reference, hypothesis):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)
    return scores

def summarize_for_ner(request):
    if request.method == 'POST':
        file_content = request.POST.get('file_content', '')

        # Generate the summary using the function
        summary_ner = utils.generate_summary_ner(file_content)

        # Calculate Rouge scores
        rouge_scores = calculate_rouge(file_content, summary_ner)

        print("Rouge-1 Precision:", rouge_scores['rouge1'].precision)
        print("Rouge-1 Recall:", rouge_scores['rouge1'].recall)
        print("Rouge-1 F1 Score:", rouge_scores['rouge1'].fmeasure)

        print("Rouge-2 Precision:", rouge_scores['rouge2'].precision)
        print("Rouge-2 Recall:", rouge_scores['rouge2'].recall)
        print("Rouge-2 F1 Score:", rouge_scores['rouge2'].fmeasure)

        print("Rouge-L Precision:", rouge_scores['rougeL'].precision)
        print("Rouge-L Recall:", rouge_scores['rougeL'].recall)
        print("Rouge-L F1 Score:", rouge_scores['rougeL'].fmeasure)

        # Extract the first four words as the title
        title_words = file_content.split()[:4]
        title = ' '.join(title_words)

        # Pass the article and summary to the template
        context = {'summary': summary_ner, 'rouge_scores': rouge_scores, 'title': title}

        return render(request, 'main/summarize.html', context)
    else:
        return render(request, 'main/summarize.html')



genai.configure(api_key="AIzaSyBeKXOpP1-_Uuxl8BseTdR19uvlAnIbGlo")

# def summarize_article_view(request):
#     title = ''
#     summary_ner = ''
#     rouge_scores = None

#     if request.method == 'POST':
#         file_content = request.POST.get('file_content', '')
#         title, summary_ner = summarize_article(file_content)

#         # Calculate Rouge scores
#         rouge_scores = calculate_rouge(file_content, summary_ner)

#         print("Rouge-1 Precision:", rouge_scores['rouge1'].precision)
#         print("Rouge-1 Recall:", rouge_scores['rouge1'].recall)
#         print("Rouge-1 F1 Score:", rouge_scores['rouge1'].fmeasure)

#         print("Rouge-2 Precision:", rouge_scores['rouge2'].precision)
#         print("Rouge-2 Recall:", rouge_scores['rouge2'].recall)
#         print("Rouge-2 F1 Score:", rouge_scores['rouge2'].fmeasure)

#         print("Rouge-L Precision:", rouge_scores['rougeL'].precision)
#         print("Rouge-L Recall:", rouge_scores['rougeL'].recall)
#         print("Rouge-L F1 Score:", rouge_scores['rougeL'].fmeasure)

#     return render(request, 'main/article_summary.html', {'title': title, 'summary_ner': summary_ner, 'rouge_scores': rouge_scores})

def generate_summary(request):
    text_input = request.POST.get('text_input', '')
    # print(f"Received text_input: {text_input}")

    defaults = {
        'model': 'models/text-bison-001',
        'temperature': 0.8,
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

    summary_genai = response.result

    content = {'summary': summary_genai}
    # print(f"Received text_input: {text_input}")
    # print(f"Generated summary: {summary}")
    # Calculate Rouge scores
    rouge_scores = calculate_rouge(text_input, summary_genai)

    print("Rouge-1 Precision:", rouge_scores['rouge1'].precision)
    print("Rouge-1 Recall:", rouge_scores['rouge1'].recall)
    print("Rouge-1 F1 Score:", rouge_scores['rouge1'].fmeasure)

    print("Rouge-2 Precision:", rouge_scores['rouge2'].precision)
    print("Rouge-2 Recall:", rouge_scores['rouge2'].recall)
    print("Rouge-2 F1 Score:", rouge_scores['rouge2'].fmeasure)

    print("Rouge-L Precision:", rouge_scores['rougeL'].precision)
    print("Rouge-L Recall:", rouge_scores['rougeL'].recall)
    print("Rouge-L F1 Score:", rouge_scores['rougeL'].fmeasure)

    # Pass the summary and Rouge scores to the template
    content = {'summary': summary_genai, 'rouge_scores': rouge_scores}

    return render(request, 'summary.html', content)