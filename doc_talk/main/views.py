from django.shortcuts import render
from . import utils

# Create your views here:
def home(request): 
    return render(request,'main/index.html')

# Function to identify and process the uploaded file
def process_uploaded_file(uploaded_file_path):
    if uploaded_file_path.endswith('.pdf'):
        # It's a PDF, read and store the text in a text file
        file_name = utils.read_pdf(uploaded_file_path)
        with open(file_name, 'r', encoding='utf-8') as txt_file:
            text = txt_file.readlines()
        return text

    elif uploaded_file_path.endswith('.txt'):
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
            return render(request, 'index.html', {'text_content': text_content})
        else:
            error_message = "Unsupported file format. Please upload a PDF or a text file."
            return render(request, 'index.html', {'error_message': error_message})
    else:
        return render(request, 'index.html')    
    

def underline_words(request):
    if request.method == 'POST':
        text = request.POST.get('input_text', '')
        words_to_underline = request.POST.get('words_to_underline', '')

        # Convert the comma-separated string of words to a list
        words_to_underline_list = [word.strip() for word in words_to_underline.split(',')]

        # Underline specified words in the text
        for word in words_to_underline_list:
            text = text.replace(word, f'<u>{word}</u>')

        return render(request, 'underline_words.html', {'input_text': text})
    else:
        return render(request, 'underline_words.html')


    
