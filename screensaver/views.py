from django.core.exceptions import PermissionDenied
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions

from backend.permissions import IsAdminOrCustomerUser

from fleet.models import User

from screensaver.models import ScreensaverMedia, ScreensaverBroadcast
from screensaver.serializers import ScreenSaverMediaSerializer, ScreenSaverBroadcastSerializer


class ScreenSaverMediaViewSet(viewsets.ModelViewSet):

    class _CustomScreenSaverMediaViewSetPermission(permissions.BasePermission):
        """
        Custom permission for ScreenSaverMediaViewSet
        """

        def has_object_permission(self, request, view, obj: ScreensaverMedia):

            if request.method == 'GET':
                return True # Allow anyone to get any screensaver

            user: User = request.user

            if user.is_customer_user():
                return obj.owner == user # Allow user to put or patch only if they are the owner of the target screensaver object

            elif user.is_staff:
                return True

            else:
                raise PermissionDenied()

    serializer_class = ScreenSaverMediaSerializer
    queryset = ScreensaverMedia.objects.none()
    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser, _CustomScreenSaverMediaViewSetPermission]

    def get_queryset(self):
        user: User = self.request.user

        if user.is_staff:
            # For admin user, we return every medias owned by an admin
            return ScreensaverMedia.objects.filter(owner__is_staff=True)

        elif user.is_customer_user():
            # For customer user, we return every medias owned by this user and every public medias
            return ScreensaverMedia.objects.filter(
                Q(owner=user) | Q(scope=ScreensaverMedia.PUBLIC_SCOPE)
            )

        else:
            raise PermissionDenied()


class ScreenSaverBroadcastViewSet(viewsets.ModelViewSet):
    serializer_class = ScreenSaverBroadcastSerializer
    queryset = ScreensaverBroadcast.objects.none()
    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser]

    def get_queryset(self):
        user: User = self.request.user

        if user.is_staff:
            # Admin user can access every broadcast of a media owned by an admin
            return ScreensaverBroadcast.objects.filter(media__owner__is_staff=True)

        if user.is_customer_user():
            # Customer user can access every broadcast to a terminal that belong to themselves
            return ScreensaverBroadcast.objects.filter(owner=user)

        else:
            raise PermissionDenied()