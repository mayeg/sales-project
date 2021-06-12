from django.urls import path

from user.views import UserView
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('', UserView.as_view()),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
