from .models import Customer, Campaign, User, DonationStep
from terminal.views import Payment
from terminal.serializers import PaymentFullSerializer
from .serializers import (
    CustomerSerializer,
    CustomerSerializerWithUser,
    UserSerializer,
    CampaignFullSerializer,
    DonationStepSerializer,
    UserSerializerWithCustomer,
)
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from backend.permissions import (
    NormalUserIsCurrentUser,
    IsAdminOrCustomerUser,
    NonAdminUserCanOnlyGet,
)
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
            serializer = UserSerializerWithCustomer(user)
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


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializerWithUser
    queryset = Customer.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated, IsAdminUser]


class ActivateCustomer(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

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
    permission_classes = [IsAuthenticated, IsAdminUser]

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
    permission_classes = [
        IsAuthenticated,
        IsAdminOrCustomerUser,
        NonAdminUserCanOnlyGet,
    ]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset().order_by("-featured", "name"), many=True, read_only=True
        )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(
            self.get_queryset().filter(is_archived=False), pk=kwargs["pk"]
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        campaign = get_object_or_404(self.get_queryset(), pk=pk)
        campaign.is_archived = True
        campaign.terminals.clear()
        campaign.save()
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAdminOrCustomerUser],
    )
    def toggle_featured(self, request, pk, format=None):
        user: User = request.user
        campaign = get_object_or_404(self.get_queryset(), pk=pk)

        if user.is_staff:
            campaign.featured = not campaign.featured
            campaign.save()

        else:
            customer = user.get_customer()
            if customer.featured_campaign == campaign:
                customer.featured_campaign = None
            else:
                customer.featured_campaign = campaign
            customer.save()

        return Response(status=status.HTTP_200_OK)


class StatsByCampaign(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, format=None):
        try:
            avg = Payment.objects.filter(campaign=id, status="Accepted").aggregate(
                Avg("amount")
            )
            total_today = Payment.objects.filter(
                campaign=id, status="Accepted", date=datetime.datetime.today()
            ).aggregate(Sum("amount"))
            total_ever = Payment.objects.filter(
                campaign=id, status="Accepted"
            ).aggregate(Sum("amount"))
            last_donations = Payment.objects.filter(
                campaign=id, status="Accepted"
            ).order_by("date")[:5]
            stats = {
                "avg_amount": avg["amount__avg"],
                "total_today": total_today["amount__sum"] or 0,
                "total_ever": total_ever["amount__sum"],
                "last_donations": PaymentFullSerializer(last_donations, many=True).data,
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
        if pk != 0:
            step = get_object_or_404(DonationStep, pk=pk)
            step.delete()
        return Response(status=status.HTTP_200_OK)
