from django.urls import path
from .views import *
urlpatterns = [
    path('auth/login/',login_with_google,name="login_user"),
    path('query/',ans_query,name="ans_query"),
    path("take_review/",get_review,name="take_review"),
    path("feedback/",get_response_feedback,name="response_feedback"),
]
