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

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

from fleet.views import *
from screensaver.views import *
from game.views import GameViewSet

from terminal.views.my_terminal import MyTerminalViewSet
from terminal.views.terminals import TerminalViewSet
from terminal.views import (
    DonatorViewSet,
    SessionViewSet,
    PaymentFilteredViewSet,
    PaymentViewSet,
    DonatorByEmail,
    StatsByTerminal,
    AvgSessionByTerminal,
    FilterSelectItems,
    DashboardStats,
    TerminalByOwner,
    PlayingOnTerminal,
    TurnOnTerminal,
    TurnOffTerminal,
    PlayingOffTerminal,
)

router = DefaultRouter()
router.register(r"customer", CustomerViewSet)
router.register(r"campaign", CampaignViewSet)
router.register(r"terminals", TerminalViewSet)
router.register(r"my-terminal", MyTerminalViewSet, basename="my_terminal")
router.register(r"donator", DonatorViewSet)
router.register(r"games", GameViewSet)
router.register(r"session", SessionViewSet)
router.register(
    r"payment/filtered", PaymentFilteredViewSet, basename="filtered_payments"
)
router.register(r"payment", PaymentViewSet)
router.register(r"screensaver-medias", ScreenSaverMediaViewSet)
router.register(r"screensaver-broadcasts", ScreenSaverBroadcastViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth", include("rest_framework.urls")),
    path("auth/token/", TokenObtainPairView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("auth/self/", UserSelf.as_view()),
    path("user/", UserList.as_view()),
    path("user/<int:pk>/", UserDetail.as_view()),
    path("donator/email/<str:email>/", DonatorByEmail.as_view()),
    path("customer/<int:pk>/activate/", ActivateCustomer.as_view()),
    path("customer/<int:pk>/deactivate/", DeactivateCustomer.as_view()),
    path("terminal/mine/", TerminalByOwner.as_view()),  # TODO remove after july 2023
    path("terminal/mine/on/", TurnOnTerminal.as_view()),  # TODO remove after july 2023
    path(
        "terminal/mine/off/", TurnOffTerminal.as_view()
    ),  # TODO remove after july 2023
    path(
        "terminal/mine/play/", PlayingOnTerminal.as_view()
    ),  # TODO remove after july 2023
    path(
        "terminal/mine/gameover/", PlayingOffTerminal.as_view()
    ),  # TODO remove after july 2023
    path("terminal/<int:terminal>/stats/", StatsByTerminal.as_view()),
    path("session/terminal/<int:terminal>/avg/", AvgSessionByTerminal.as_view()),
    path("campaign/<int:id>/stats/", StatsByCampaign.as_view()),
    path("campaign/<int:id>/full/", StatsByCampaign.as_view()),
    path("campaigns/full/", StatsByCampaign.as_view()),
    path("donationstep/<int:pk>/", UpdateDonationStep.as_view()),
    path("donationstep/", CreateDonationStep.as_view()),
    path("donationstep/<int:pk>/delete/", DeleteDonationStep.as_view()),
    path("game/", include("game.urls")),
    path("dashboard/", DashboardStats.as_view()),
    path("payment/SelectItems/", FilterSelectItems.as_view()),
]

urlpatterns += router.urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
