from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,permission_classes
from django.http import JsonResponse, FileResponse
from rest_framework import status
import requests,os
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from django.core.mail import send_mail
from rest_framework.response import Response
from .services import welcome_html
from django.db import transaction

import httpagentparser


AI_SERVER_URL="http://127.0.0.1:8888/"

@api_view(["POST"])
@csrf_exempt
def login_with_google( request):
    token=request.POST["token"]
    if not token:
        return Response({"error": "Token not provided","status":False}, status=status.HTTP_400_BAD_REQUEST)
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_OAUTH2_CLIENT_ID)

        email = id_info['email']
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        given_name = id_info.get('given_name', '')
        profile_pic_url = id_info.get('picture', '')
        

        user, created = CustomUser.objects.get_or_create(email=email, defaults={
            'first_name': first_name,
            'last_name': last_name,
            'email_verified':True,
            'profile_pic_url':profile_pic_url
        })

        if created:
            user.set_unusable_password()
            user.save()
            html=welcome_html(user)
            send_mail(
                "CSGPT Welcome's You",
                    ' ', 
                "csgptmail@gmail.com",
                [email], 
                html_message=html
                )

        access_token = str(RefreshToken.for_user(user).access_token)
        return Response(
            {
            "access": access_token,
            "status":True
            }, 
        status=status.HTTP_200_OK
        )

    except ValueError as e:
        return Response({"error": "Invalid token","status":False}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def ans_query(request):
    question=request.data.get("question")
    user_id=request.user.id
    agent=request.META["HTTP_USER_AGENT"]
    s = httpagentparser.detect(agent)
    operating_sytem,broswer=s['os']['name'],s['browser']['name']
    resp=requests.post(AI_SERVER_URL+"query/",json={'question':question,"user_id":user_id,"os":operating_sytem,"browser":broswer})
    # resp=requests.post(AI_SERVER_URL+"query/",json={'question':question,"user_id":user_id,"os":"operating_sytem","browser":"broswer"})
    if resp.status_code==200:
        data=resp.json()['markdown_data']
        return JsonResponse(
            {'data':data,"server_status":True},status=200
        )
    return JsonResponse(
            {"server_status":False,'data':"Ooops We are down try in 5 mins"},status=200
        )

@transaction.atomic
@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_review(request):
    user:CustomUser=request.user
    try:
        name,email=user.first_name,user.email
        feedback=request.data.get('feedback')
        stars=request.data.get('stars')
        review=Review(name=name,email=email,feedback=feedback,stars=stars)
        review.save()
        return JsonResponse({"mssg":"Review saved successfully...."},status=200)
    except:
        return JsonResponse({"mssg":"Problem saving review...."},status=status.HTTP_400_BAD_REQUEST)
    
@transaction.atomic
@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_response_feedback(request):
    try:
        data=request.data
        feedback=data.get('Response Feedback')
        user=request.user
        if feedback==1:
            resp_feedback=ResponseFeedback.objects.create(user=user,like=1)
        else:
            resp_feedback=ResponseFeedback.objects.create(user=user,dislike=1)
        resp_feedback.save()
        return JsonResponse({"mssg":"Feedback added successfully...."},status=200)
    except:
        return JsonResponse({"mssg":"Failed to add feedback"},status=status.HTTP_400_BAD_REQUEST)

