from django.urls import path
from .views import *

urlpatterns = [
    path('', GameListView.as_view()),
    path('create/', GameCreateView.as_view()),
    path('<int:pk>/', GameRetrieveUpdateDestroyView.as_view()),
    path('<int:pk>/update/', GameUpdateView.as_view()),
    path('upload/', GameFileUploadView.as_view()),
    path('core/upload/', CoreFileUploadView.as_view()),
]