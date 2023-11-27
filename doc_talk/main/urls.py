# URLs inside Main App: 

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "home-page"),
<<<<<<< HEAD
    path("notes", views.ner, name= "home-page"),
    path("upload_doc",views.document , name = "doc-upload"),
    path("ner",views.underline_words , name = "word-underline"),
    path('main/generate_summary/', views.generate_summary, name='generate_summary'),
=======
    path("/notes", views.ner, name= "home-page"),
    path("/upload_doc",views.document , name = "doc-upload"),
    path("/ner",views.underline_words , name = "word-underline"),
    path("/summarize",views.summarize_article , name = "summary")
>>>>>>> 4a69b6ec6cde9c999802cc7e51a63ba940c925c0
]