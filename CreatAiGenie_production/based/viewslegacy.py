import os
import logging
from django.views.generic import TemplateView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .models import UserProfile, Document, ProcessedData, SubscriptionPlan, UserSubscription, Signagetemp, SignageSubCategory, SignageCategory
from .serializers import (
    TextSerializer, PromptSerializer, FileSerializer, 
    UserSerializer, UserProfileSerializer, DocumentSerializer, 
    ProcessedDataSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer,
    SignagetempSerializer, KeywordSerializer, SignageCategorySerializer, SignageSubCategorySerializer,
)
from utils.keywordexactor import KeywordExtractionView
from utils.utils import summarize_text, generate_image_from_text, extract_text_from_file
from amazonapis.ad_group_report import AdGroupReport

logger = logging.getLogger(__name__)
User = get_user_model()

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tabs'] = [
            {'id': 'SummarizeText', 'title': 'Summarize Text'},
            {'id': 'GenerateImage', 'title': 'Generate Image'},
            {'id': 'KeywordExtraction', 'title': 'Keyword Extractor'},
            {'id': 'UploadFile', 'title': 'Upload File'},
            {'id': 'Signagetemplate', 'title': 'Signage Template'},
            {'id': 'SignagetempDetail', 'title': 'Signage Template by ID'},
        ]
        return context

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all() 
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_all_users(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class SummarizeTextView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TextSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        text = serializer.validated_data['text']
        try:
            summary = summarize_text(text)
            return Response({'summary-result': summary}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in SummarizeTextView: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateImageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PromptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        prompt = serializer.validated_data['prompt']
        try:
            image_url = generate_image_from_text(prompt)
            if image_url:
                return Response({'image_url': image_url}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to generate image.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in GenerateImageView: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KeywordExtractView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ad_copy = request.data.get('ad_copy')
        if not ad_copy:
            logger.warning(f"Missing ad_copy in request: {request.data}")
            return Response({"error": "Ad copy is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            keyword_extractor = KeywordExtractionView()
            keywordslist = keyword_extractor.extract_keywords_using_openai(ad_copy)

            if keywordslist:
                return Response({'keywords': keywordslist}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to generate keywords.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in KeywordExtractView: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
     
class FileUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        print(request.META.get('HTTP_AUTHORIZATION'))  # Log or print the Authorization header
        serializer = FileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file = serializer.validated_data['file']
        try:
            text = extract_text_from_file(file)
            if text:
                summary = summarize_text(text)
                return Response({'text': text, 'summary': summary}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to extract text from file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in FileUploadView: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SignagetempListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = 10
            signagetemps = Signagetemp.objects.all()
            paginated_signagetemps = paginator.paginate_queryset(signagetemps, request)
            serializer = SignagetempSerializer(paginated_signagetemps, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving signage templates: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class SignagetempDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            signagetemp = Signagetemp.objects.get(pk=pk)
        except Signagetemp.DoesNotExist:
            return Response({"error": "Signage template not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SignagetempSerializer(signagetemp)

        try:
            if serializer.data:
                return Response({'signage_template': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to retrieve signage template.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error retrieving signage template: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

class ProcessedDataViewSet(viewsets.ModelViewSet):
    queryset = ProcessedData.objects.all()
    serializer_class = ProcessedDataSerializer
    permission_classes = [IsAuthenticated]

class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]
