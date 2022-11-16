from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.permissions import IsAdminOrCustomerUser
from fleet import serializers

from fleet.models import User

from screensaver.models import ScreensaverMedia, ScreensaverBroadcast
from screensaver.serializers import ScreenSaverMediaSerializer, ScreenSaverBroadcastSerializer


class ScreenSaverMediaViewSet(viewsets.ModelViewSet):

    class _CustomPermission(permissions.BasePermission):
        """
        Custom permission for ScreenSaverMediaViewSet
        """

        def has_object_permission(self, request, view, obj: ScreensaverMedia):

            user: User = request.user

            if user.is_customer_user():
                if request.method == 'GET':
                    # Allow user to fetch media only if they are the owner or if the media is public
                    return obj.scope == obj.PUBLIC_SCOPE or obj.owner == user 

                else:
                    # Allow user to put, post or delete media only if they are the owner
                    return obj.owner == user and user.get_customer().can_edit_screensaver_broadcasts

            elif user.is_staff:
                # Allow staff member to fetch, post, put or delete media only if this media belong to a staff member or if this media is public
                return obj.scope == obj.PUBLIC_SCOPE or obj.owner.is_staff 

            else:
                raise PermissionDenied()

    serializer_class = ScreenSaverMediaSerializer
    queryset = ScreensaverMedia.objects.none()
    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser, _CustomPermission]

    def get_queryset(self):
        user: User = self.request.user

        if user.is_staff:
            # Allow staff member to fetch, media only if this media belong to a staff member or if this media is public
            return ScreensaverMedia.objects.filter(Q(owner__is_staff=True) | Q(scope=ScreensaverMedia.PUBLIC_SCOPE))

        elif user.is_customer_user():
            # Allow user to fetch media only if they are the owner or if the media is public
            return ScreensaverMedia.objects.filter(
                Q(owner=user) | Q(scope=ScreensaverMedia.PUBLIC_SCOPE)
            )

        else:
            raise PermissionDenied()


class ScreenSaverBroadcastViewSet(viewsets.ModelViewSet):

    class _CustomPermission(permissions.BasePermission):
        """
        Custom permission for ScreenSaverBroadcastViewSet
        """

        def has_object_permission(self, request, view, obj: ScreensaverMedia):

            user: User = request.user

            if user.is_customer_user():
                if request.method == 'GET':
                    return obj.terminal.customer == user.get_customer()

                else:
                    return obj.terminal.customer == user.get_customer() and user.get_customer().can_edit_screensaver_broadcasts

            elif user.is_staff:
                # Allow staff member to fetch, post, put or delete media only if this media belong to a staff member or if this media is public
                return obj.media.scope == obj.PUBLIC_SCOPE or obj.media.owner.is_staff

            else:
                raise PermissionDenied()

    queryset = ScreensaverBroadcast.objects.none()
    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser, _CustomPermission]
    serializer_class = ScreenSaverBroadcastSerializer

    def get_queryset(self):
        user: User = self.request.user

        if user.is_staff:
            # Admin user can access every broadcast of a media owned by an admin
            return ScreensaverBroadcast.objects.filter(media__owner__is_staff=True)

        if user.is_customer_user():
            # Customer user can access every broadcast to a terminal that belong to themselves
            return ScreensaverBroadcast.objects.filter(terminal__customer=user.get_customer())

        else:
            raise PermissionDenied()


    @action(detail=True, methods=['post'])
    def activate(self, request, pk):
        broadcast = get_object_or_404(self.get_queryset(), pk=pk)

        broadcast.visible = True
        broadcast.save()

        serializer = ScreenSaverBroadcastSerializer(broadcast)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk):
        broadcast = get_object_or_404(self.get_queryset(), pk=pk)

        broadcast.visible = False
        broadcast.save()

        serializer = ScreenSaverBroadcastSerializer(broadcast)
        return Response(serializer.data)