from django.urls import path
from .views import *

urlpatterns = [
    path('core/', CoreListView.as_view()),
    path('core/create/', CoreCreateView.as_view()),
    path('core/<int:pk>/', CoreRetrieveDestroyView.as_view()),
    path('core/<int:pk>/update/', CoreUpdateView.as_view()),
    path('core/upload/', CoreFileUploadView.as_view()),
    path('core/bios/upload/', BiosFileUploadView.as_view()),
]