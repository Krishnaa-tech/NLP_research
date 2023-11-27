# URLs inside Main App: 

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "home-page"),
    path("/notes", views.home, name= "home-page"),
    path("/ner",views.document , name = "doc-upload"),
    path("/ner",views.underline_words , name = "word-underline")
]