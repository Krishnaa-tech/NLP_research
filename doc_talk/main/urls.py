# URLs inside Main App: 

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "home-page"),
    path("notes", views.ner, name= "home-page"),
    path("upload_doc",views.document , name = "doc-upload"),
    path("ner",views.underline_words , name = "word-underline"),
    path('main/generate_summary/', views.generate_summary, name='generate_summary'),
]