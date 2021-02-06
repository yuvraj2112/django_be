from django.urls import path
from buyer import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('login', views.BuyerLogin.as_view()),
    path('cart', views.BuyerCart.as_view()),
    path('cart/<str:key>', views.BuyerCart.as_view()),
    path('order/<str:token>', views.BuyerOrder.as_view()),
    path('store', views.BuyerStore.as_view()),
    path('products', views.BuyerProducts.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)