from django.urls import path
from . import views
from .views import ProductView, CategoryView


urlpatterns = [
    path('', views.index),
    path('products/<str:id>/', ProductView.as_view(), name='products-detail'),
    path('products/', ProductView.as_view(), name='products-list'),
    path('categories/<str:id>/', CategoryView.as_view(), name='categories-detail'),
    path('categories/', CategoryView.as_view(), name='categories-list'),
]