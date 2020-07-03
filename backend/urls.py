"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fleet.views import *
from terminal.views import *
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'customer', CustomerViewSet)
router.register(r'campaign', CampaignViewSet)
router.register(r'game', GameViewSet)
router.register(r'terminal', TerminalViewSet)
router.register(r'donator', DonatorViewSet)
router.register(r'session', SessionViewSet)
router.register(r'payment', PaymentViewSet)

urlpatterns = [
    path('api-auth', include('rest_framework.urls')),
    path('auth/', CustomObtainAuthToken.as_view()),
    path('user/', UserList.as_view()),
    path('user/<int:pk>/', UserDetail.as_view()),
    path('donator/email/<str:email>/', DonatorByEmail.as_view()),
    path('customer/<int:pk>/activate/', ActivateCustomer.as_view()),
    path('customer/<int:pk>/deactivate/', DeactivateCustomer.as_view()),
    path('terminal/<int:pk>/activate/', ActivateTerminal.as_view()),
    path('terminal/<int:pk>/deactivate/', DeactivateTerminal.as_view()),
    path('terminal/<int:pk>/campaigns/', CampaignsByTerminal.as_view()),
    path('terminal/<int:pk>/games/', GamesByTerminal.as_view()),
    path('terminal/mine/', TerminalByOwner.as_view()),
    path('terminal/mine/on/', TurnOnTerminal.as_view()),
    path('terminal/mine/off/', TurnOffTerminal.as_view()),
    path('terminal/mine/play/', PlayingOnTerminal.as_view()),
    path('terminal/mine/gameover/', PlayingOffTerminal.as_view()),
    path('terminal/<int:terminal>/stats/', StatsByTerminal.as_view()),
    path('session/terminal/<int:terminal>/avg/', AvgSessionByTerminal.as_view()),
    path('campaign/<int:id>/stats/', StatsByCampaign.as_view()),
    path('campaign/<int:id>/full/', StatsByCampaign.as_view()),
    path('campaigns/full/', StatsByCampaign.as_view()),
    path('dashboard/', DashboardStats.as_view())
]

urlpatterns += router.urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)