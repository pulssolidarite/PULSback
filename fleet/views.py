from .models import Customer, Campaign, User, DonationStep
from django.conf import settings
from terminal.views import Terminal, Payment
from terminal.serializers import PaymentFullSerializer
from .serializers import CustomerSerializer, CampaignSerializer, UserSerializer, CampaignFullSerializer, DonationStepSerializer
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import action
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


class UserSelf(APIView):
    def get(self, request, format=None):
        try:
            print(request.user)
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

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


class CustomerDetailByUser(APIView):
    # TODO deprecated, Customer is directly returned from terminal view
    # This should be removed

    user_queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        user = get_object_or_404(self.user_queryset, pk=user_id)
        self.check_object_permissions(self.request, user)

        customer = user.get_terminal().customer if user.get_terminal() else None

        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)



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


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignFullSerializer
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated, NormalUserListRetrieveOnly]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset().order_by("-featured", "name"), many=True, read_only=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset().filter(is_archived=False), pk=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs): # TODO get is never called in ModelViewSet, should be list() ?
        serializer = CampaignSerializer(self.get_queryset(), context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        campaign = get_object_or_404(self.get_queryset(), pk=pk)
        campaign.is_archived = True
        campaign.terminals.clear()
        campaign.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def featured(self, request, pk, format=None):
        campaign = get_object_or_404(self.get_queryset(), pk=pk)
        campaign.featured = True
        campaign.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def not_featured(self, request, pk, format=None):
        campaign = get_object_or_404(self.get_queryset(), pk=pk)
        campaign.featured = False
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

# post request
class CreateDonationStep(generics.CreateAPIView):
    queryset = DonationStep.objects.all()
    serializer_class = DonationStepSerializer
    permission_classes = [IsAdminUser]

# patch request
class UpdateDonationStep(generics.UpdateAPIView):
    queryset = DonationStep.objects.all()
    serializer_class = DonationStepSerializer
    permission_classes = [IsAdminUser]

# delete request
class DeleteDonationStep(APIView):
    queryset = DonationStep.objects.all()
    serializer_class = DonationStepSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        if (pk != 0):
            step = get_object_or_404(DonationStep, pk=pk)
            step.delete()
        return Response(status=status.HTTP_200_OK)


