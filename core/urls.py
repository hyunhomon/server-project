from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.login),
    path('register/', views.register),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('user/info/', views.get_user_info),
    path('user/follows/', views.get_user_follows),
    path('user/notifications/', views.get_user_notifications),
    path('user/categories/', views.get_user_categories),
    path('follow/add/', views.add_follow),
    path('follow/del/', views.del_follow),
    path('category/add/', views.add_category),
    path('category/mod/', views.mod_category)
]
