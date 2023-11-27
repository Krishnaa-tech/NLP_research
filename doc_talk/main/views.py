from django.shortcuts import render
from . import utils

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


    
