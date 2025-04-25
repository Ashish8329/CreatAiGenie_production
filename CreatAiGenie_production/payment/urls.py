from django.urls import path, include, re_path
from .views import CreateOrderApiView

urlpatterns = [
    path('', CreateOrderApiView.as_view(), name='create-order'),
]


