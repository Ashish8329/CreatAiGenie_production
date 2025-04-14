from django.urls import path, include
from rest_framework import routers
from src.settings import * 
from django.conf.urls.static import static
from .views import ( 
                    HomeView,
                    FileUploadView, 
                    SummarizeTextView,
                    GenerateImageView,
                    KeywordExtractionView,
                    UserViewSet,
                    UserProfileViewSet,
                    DocumentViewSet,
                    ProcessedDataViewSet,
                    SubscriptionPlanViewSet,
                    UserSubscriptionViewSet,
                    SignagetempListView,
                    SignagetempDetailView)

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('user-profiles', UserProfileViewSet)
router.register('documents', DocumentViewSet)
router.register('processed-data', ProcessedDataViewSet)
router.register('subscription-plans', SubscriptionPlanViewSet)
router.register('user-subscriptions', UserSubscriptionViewSet)

urlpatterns = [
    path('basedapi/', include(router.urls)),
    path('', HomeView.as_view(), name='home'),
    path('summarize-text/', SummarizeTextView.as_view(), name='summary-result'),
    path('generate-image/', GenerateImageView.as_view(), name='generate_image'),
    path('extract-keywords/', KeywordExtractionView.as_view(), name='extract_keywords'),
    path('upload-file/', FileUploadView.as_view(), name='upload_file'),    
    path('signagetemps/', SignagetempListView.as_view(), name='signagetemp-list'),
    path('signagetempsid/<int:pk>/', SignagetempDetailView.as_view(), name='signagetemp-detail'),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)


'''
curl -X POST http://127.0.0.1:8000/auth/jwt/create/ \
     -H "Content-Type: application/json" \
     -d '{"email": "sidpawar1155@gmail.com", "password": "admin"}'

curl -X POST http://127.0.0.1:8000/summarize-text/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text to summarize here"}'


curl -X POST http://127.0.0.1:8000/generate-image/ \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIzNTYyMDE4LCJpYXQiOjE3MjM1NTg0MTgsImp0aSI6IjMxMWYzN2FmOThkNTRmZDBiMDQ3ZjEwZTc2NmFmOTU2IiwidXNlcl9pZCI6MX0.PlWQRJlKUGnf1eBf4mKkYkwhcXVjlh5QZ9Qbb3c0mf0" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Your image description here"}'

curl -X POST http://127.0.0.1:8000/upload-file/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -F "file=@/path/to/your/file"

'''