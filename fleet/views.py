from .models import Customer, Campaign, User
from django.conf import settings
from terminal.views import Terminal, Payment
from terminal.serializers import PaymentFullSerializer
from .serializers import CustomerSerializer, CampaignSerializer, UserSerializer, CampaignFullSerializer
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from backend.permissions import IsSuperStaff, NormalUserListRetrieveOnly, NormalUserIsCurrentUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Sum
from rest_framework.views import APIView
from rest_framework import status
import json
import datetime


# User Model
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [NormalUserIsCurrentUser]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


# Customer Model
class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.filter(is_archived=False)
    permission_classes = [IsAdminUser]


class ActivateCustomer(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk, format=None):
        try:
            customer = Customer.objects.get(pk=pk)
            customer.is_active = True
            customer.save()
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class DeactivateCustomer(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk, format=None):
        try:
            customer = Customer.objects.get(pk=pk)
            customer.is_active = False
            customer.save()
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# Campaign Model
class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignFullSerializer
    queryset = Campaign.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated, NormalUserListRetrieveOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Campaign, pk=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        queryset = Campaign.objects.filter(is_archived=False)
        serializer = CampaignSerializer(queryset, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        campaign = get_object_or_404(Campaign, pk=pk)
        campaign.is_archived = True
        campaign.terminals.clear()
        campaign.save()
        return Response(status=status.HTTP_200_OK)


class StatsByCampaign(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, format=None):
        try:
            avg = Payment.objects.filter(campaign=id, status="Accepted").aggregate(Avg('amount'))
            total_today = Payment.objects.filter(campaign=id, status="Accepted", date=datetime.datetime.today()).aggregate(Sum('amount'))
            total_ever = Payment.objects.filter(campaign=id, status="Accepted").aggregate(Sum('amount'))
            last_donations = Payment.objects.filter(campaign=id, status="Accepted").order_by('date')[:5]
            stats = {
                'avg_amount': avg['amount__avg'],
                'total_today': total_today['amount__sum'] or 0,
                'total_ever': total_ever['amount__sum'],
                'last_donations': PaymentFullSerializer(last_donations, many=True).data
            }
            serializer = json.dumps(stats)
            return Response(serializer, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# Obtain Token
class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = get_object_or_404(User, username=request.data['username'])
        return Response({'token': token.key, 'user_id': user.id, 'is_admin': user.is_staff, 'is_superadmin': user.is_admin})
