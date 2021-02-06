from django.urls import path
from seller import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('login', views.SellerLogin.as_view()),
    path('stores/<str:token>', views.SellerStores.as_view()),
    path('product/<str:token>', views.SellerProducts.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)