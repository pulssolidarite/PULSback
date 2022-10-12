import datetime
import json
import csv
import os
import sys

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import Paginator


from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from game.models import Game

from fleet.models import Customer, User
from fleet.serializers import CustomerSerializer, CampaignSerializer

from backend.permissions import IsAdminOrCustomerUser

from .models import Terminal, Donator, Session, Payment,Campaign
from .serializers import *


# Terminal Model
class TerminalViewSet(viewsets.ModelViewSet):
    """
    This view is used from SETH front admin or customer
    """

    queryset = Terminal.objects.filter(is_archived=False)
    serializer_class = FullTerminalSerializer

    def get_queryset(self):
        user: User = self.request.user

        if user.is_customer_user():
            return Terminal.objects.filter(is_archived=False, customer=user.get_customer()) # For customer, return all terminals that belong to this customer

        elif user.is_staff:
            return Terminal.objects.filter(is_archived=False)

        else:
            raise PermissionDenied()

    def get_permissions(self):
        """
        Allow admin and customers to list, retrieve and update but only admin to do any other actions
        
        """
        if self.action == "list" or self.action == "retrieve" or self.action == "update":
            permission_classes = [IsAuthenticated, IsAdminOrCustomerUser]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        serializer = TerminalSemiSerializer(self.get_queryset(), many=True, read_only=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def activate(self, request, pk, format=None):
        terminal = get_object_or_404(self.get_queryset(), pk=pk)
        terminal.is_active = True
        terminal.owner.is_active = True
        terminal.save()
        terminal.owner.save()
        serializer = FullTerminalSerializer(terminal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def deactivate(self, request, pk, format=None):
        terminal = get_object_or_404(self.get_queryset(), pk=pk)
        terminal.is_active = False
        terminal.owner.is_active = False
        terminal.is_on = False
        terminal.is_playing = False
        terminal.save()
        terminal.owner.save()
        serializer = FullTerminalSerializer(terminal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def archive(self, request, pk, format=None):
        terminal = get_object_or_404(self.get_queryset(), pk=pk)
        terminal = Terminal.objects.get(pk=pk)
        terminal.is_active = False
        terminal.owner.is_active = False
        terminal.is_archived = True
        terminal.save()
        terminal.owner.save()
        serializer = FullTerminalSerializer(terminal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def campaigns(self, request, pk, format=None):
        terminal = get_object_or_404(self.get_queryset(), pk=pk)
        campaigns = terminal.campains
        serializer = CampaignSerializer(campaigns, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def games(self, request, pk, format=None):
        terminal = get_object_or_404(self.get_queryset(), pk=pk)
        games = terminal.games
        games = GameSerializer(games, many=True, context={"request": request})
        return Response(games.data, status=status.HTTP_200_OK)
       


class DashboardStats(APIView):
    """
    This view is used from SETH front admin or customer
    """

    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser] # Only accessible for admin or customer users

    def get(self, request, format=None):
        user: User = request.user

        campaigns = Campaign.objects.all()
        campaigns_serlializer = CampaignSerializer(campaigns, many=True, context={"request": request})

        if user.is_customer_user():
            terminals = Terminal.objects.filter(is_on=True, customer=user.get_customer())
            terminals = TerminalSemiSerializer(terminals, many=True, context={"request": request})

            collected = Payment.objects.filter(terminal__customer=user.get_customer(), date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
            collected_last = Payment.objects.filter(terminal__customer=user.get_customer(), date__month=datetime.datetime.now().month - 1, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
            
            donated = Payment.objects.filter(terminal__customer=user.get_customer(), date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).aggregate(Sum('amount_donated'))['amount__sum']
            donated_last = Payment.objects.filter(terminal__customer=user.get_customer(), date__month=datetime.datetime.now().month - 1, date__year=datetime.datetime.now().year).aggregate(Sum('amount_donated'))['amount__sum']
            
            nb_donators = Session.objects.filter(terminal__customer=user.get_customer(), start_time__month=datetime.datetime.now().month, start_time__year=datetime.datetime.now().year).count()
            nb_donators_last = Session.objects.filter(terminal__customer=user.get_customer(), start_time__month=datetime.datetime.now().month - 1, start_time__year=datetime.datetime.now().year).count()

            nb_terminals = Terminal.objects.filter(customer=user.get_customer()).count()
            
            total_gamesession = Session.objects.filter(terminal__customer=user.get_customer()).aggregate(Sum('timesession'))['timesession__sum']
           
            return Response(
                {
                    'terminals': terminals.data,
                    'campaigns': campaigns_serlializer.data,
                    'collected': collected,
                    'collected_last': collected_last,
                    'donated': donated,
                    'donated_last': donated_last,
                    'nb_donators': nb_donators,
                    'nb_terminals': nb_terminals,
                    'total_gamesession': total_gamesession,
                    'nb_donators_last': nb_donators_last
                }, status=status.HTTP_200_OK
            )

        elif user.is_staff:
            terminals = Terminal.objects.filter(is_on=True)
            terminals = TerminalSemiSerializer(terminals, many=True, context={"request": request})

            collected = Payment.objects.filter(date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
            collected_last = Payment.objects.filter(date__month=datetime.datetime.now().month - 1, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']

            donated = Payment.objects.filter(terminal__customer=user.get_customer(), date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).aggregate(Sum('amount_donated'))['amount__sum']
            donated_last = Payment.objects.filter(terminal__customer=user.get_customer(), date__month=datetime.datetime.now().month - 1, date__year=datetime.datetime.now().year).aggregate(Sum('amount_donated'))['amount__sum']

            nb_donators = Session.objects.filter(start_time__month=datetime.datetime.now().month, start_time__year=datetime.datetime.now().year).count()
            nb_donators_last = Session.objects.filter(start_time__month=datetime.datetime.now().month - 1, start_time__year=datetime.datetime.now().year).count()

            nb_terminals = Terminal.objects.all().count()

            total_gamesession = Session.objects.all().aggregate(Sum('timesession'))['timesession__sum']

            return Response(
                {
                    'terminals': terminals.data,
                    'campaigns': campaigns_serlializer.data,
                    'collected': collected,
                    'collected_last': collected_last,
                    'donated': donated,
                    'donated_last': donated_last,
                    'nb_donators': nb_donators,
                    'nb_terminals': nb_terminals,
                    'total_gamesession': total_gamesession,
                    'nb_donators_last': nb_donators_last,
                }, status=status.HTTP_200_OK
            )

        else:
            raise PermissionDenied()




class FilterSelectItems(APIView):
    """
    This view is used from SETH front admin or customer
    """

    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser] # Only accessible for admin or customer users

    def get(self, request, format=None):

        user: User = request.user

        campaigns = Campaign.objects.filter().order_by("name")
        campaigns_serlializer = CampaignSerializer(campaigns, many=True, context={"request": request})

        games = Game.objects.filter().order_by("name")
        games_serlializer = GameSerializer(games, many=True, context={"request": request})

        if user.is_customer_user():
            terminals = Terminal.objects.filter(customer=user.get_customer())
            terminals = TerminalSemiSerializer(terminals, many=True, context={"request": request})
            return Response({'terminals': terminals.data, 'campaigns': campaigns_serlializer.data, 'games' : games_serlializer.data }, status=status.HTTP_200_OK)

        elif user.is_staff:
            terminals = Terminal.objects.all()
            terminals = TerminalSemiSerializer(terminals, many=True, context={"request": request})
            customers = Customer.objects.filter().order_by("company")
            customers = CustomerSerializer(customers, many=True, context={"request": request})
            return Response({'terminals': terminals.data, 'campaigns': campaigns_serlializer.data, 'games' : games_serlializer.data, 'customers' : customers.data }, status=status.HTTP_200_OK)
        
        else:
            raise PermissionDenied()






class PaymentFilteredViewSet(viewsets.ViewSet):
    """
    This view is used from SETH front admin or customer
    """

    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser] # Only accessible for admin or customer users

    class _PaymentWithoutDonatorSerializer(serializers.ModelSerializer):

    
        class _TerminalSerializer(serializers.ModelSerializer):

            class _CustomerSerializer(serializers.ModelSerializer):
                class Meta:
                    model = Customer
                    fields = ("company",)

            customer = _CustomerSerializer(many=False, read_only=True)
            class Meta:
                model = Terminal
                fields = ("id", "name", "customer", "payment_terminal", "donation_formula",)

        class _CampaignSerializer(serializers.ModelSerializer):
            class Meta:
                model = Campaign
                fields = ("name",)

        class _GameSerializer(serializers.ModelSerializer):
            class Meta:
                model = Game
                fields = ("name",)

        terminal = _TerminalSerializer(many=False, read_only=True)
        campaign = _CampaignSerializer(many=False, read_only=True)
        game = _GameSerializer(many=False, read_only=True)

        class Meta:
            model = Payment
            fields = ("id", "date", "status", "terminal", "campaign", "game", "amount",)

    class _PaymentWithDonatorSerializer(_PaymentWithoutDonatorSerializer):

        class _DonatorSerializer(serializers.ModelSerializer):
            class Meta:
                model = Donator
                fields = ("email", "accept_newsletter", "accept_asso",)

        donator = _DonatorSerializer(many=False, read_only=True)

        class Meta:
            model = Payment
            fields = ("id", "date", "status", "donator", "terminal", "campaign", "game", "amount",)

    def _get_filtred_payments(self, request):
        """
        Return a queryset of Payment objects

        Possible query params :
        - campaign
        - terminal
        - customer
        - status
        - game
        - date
        - date_start
        - date_end
        - payment_terminal
        - donation_formula
        """

        # Fetch params
        
        campaign_id = self.request.query_params.get('campaign')
        terminal_id = self.request.query_params.get('terminal')
        customer_id = self.request.query_params.get('customer')
        donation_formula = self.request.query_params.get('donation_formula')
        payment_status = self.request.query_params.get('payment_status')
        game_id = self.request.query_params.get('game')
        date = self.request.query_params.get('date')
        date_start = self.request.query_params.get('start_date')
        date_end = self.request.query_params.get('end_date')
        payment_terminal = self.request.query_params.get('payment_terminal')  

        # Query payments (all payments if logged user is admin, only customer payments if logged user is customer)

        user: User = request.user

        payments = Payment.objects.none()

        if user.is_staff:
            payments = Payment.objects.all()

        elif user.is_customer_user():
            payments = Payment.objects.filter(terminal__customer=user.get_customer())

        else:
            raise PermissionDenied()
        
        # Filter by terminals

        if terminal_id:
            payments = payments.filter(terminal_id=terminal_id)

        # Filter by customer

        if customer_id:
            payments = payments.filter(terminal__customer_id=customer_id)

        # Filter by campaign

        if campaign_id:
            payments = payments.filter(campaign_id=campaign_id)

        # Filter by game

        if game_id:
            payments = payments.filter(game_id=game_id)

        # Filter by payment_status

        if payment_status:
            payments = payments.filter(status=payment_status)

        # Filter by donation_formula

        if donation_formula:
            payments = payments.filter(donation_formula=donation_formula)

        # Filter by payment_terminal

        if payment_terminal:
            payments = payments.filter(payment_terminal=payment_terminal)

        # Filter by date_start

        if date_start:
            formatted_date = date_start.replace('T', ' ')
            converted_date_start =  datetime.datetime.strptime(formatted_date, '%d-%m-%Y %H:%M:%S')
            payments = payments.filter(date__gte=converted_date_start)

        # Filter by date_end

        if date_end:
            formatted_date = date_end.replace('T', ' ')
            converted_date_end =  datetime.datetime.strptime(formatted_date, '%d-%m-%Y %H:%M:%S')
            payments = payments.filter(date__lt=converted_date_end)

        # Filter by date (period)

        today = datetime.date.today()

        if date == "Today":
            tomorrow = today + datetime.timedelta(1)
            today_start = datetime.datetime.combine(today, datetime.time())
            tomorrow_start = datetime.datetime.combine(tomorrow, datetime.time())

            payments = payments.filter(date__gte=today_start, date__lt=tomorrow_start)

        elif date == "Yesterday":
            today_start = datetime.datetime.combine(today, datetime.time())
            
            yesterday = today + datetime.timedelta(-1)
            yesterday_start = datetime.datetime.combine(yesterday, datetime.time())

            payments = payments.filter(date__gte=yesterday_start, date__lt=today_start)

        elif date == "7days":
            tomorrow = today + datetime.timedelta(1)
            tomorrow_start = datetime.datetime.combine(tomorrow, datetime.time())

            seven_days_ago = today + datetime.timedelta(-7)
            seven_days_ago_start = datetime.datetime.combine(seven_days_ago, datetime.time())

            payments = payments.filter(date__gte=seven_days_ago_start, date__lt=tomorrow_start)

        elif date == "CurrentWeek":
            tomorrow = today + datetime.timedelta(1)
            tomorrow_start = datetime.datetime.combine(tomorrow, datetime.time())

            monday_of_this_week = today - datetime.timedelta(days=today.weekday())
            monday_of_this_week_start = datetime.datetime.combine(monday_of_this_week, datetime.time())

            payments = payments.filter(date__gte=monday_of_this_week_start, date__lt=tomorrow_start)

        elif date == "LastWeek":
            some_day_last_week = today - datetime.timedelta(days=7)
            monday_of_last_week = some_day_last_week - datetime.timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
            monday_of_last_week_start = datetime.datetime.combine(monday_of_last_week, datetime.time())
            
            monday_of_this_week = today - datetime.timedelta(days=today.weekday())
            monday_of_this_week_start = datetime.datetime.combine(monday_of_this_week, datetime.time())

            payments = payments.filter(date__gte=monday_of_last_week_start, date__lt=monday_of_this_week_start)

        elif date == "CurrentMonth":
            start_month = datetime.datetime(today.year, today.month, 1)
            date_on_next_month = start_month + datetime.timedelta(35)
            start_next_month = datetime.datetime(date_on_next_month.year, date_on_next_month.month, 1)

            payments = payments.filter(date__gte=start_month, date__lt=start_next_month)

        elif date == "LastMonth":
            first = today.replace(day=1)  # first date of current month
            end_previous_month = first - datetime.timedelta(days=1)
            start_previous_month = end_previous_month.replace(day=1)

            start_this_month = datetime.datetime(today.year, today.month, 1)

            payments = payments.filter(date__gte=start_previous_month, date__lt=start_this_month)

        elif date == "ThisYear":
            first_day_of_this_year = today.replace(day=1, month=1)
            first_day_of_this_year_begining = datetime.datetime.combine(first_day_of_this_year, datetime.time())

            last_day_of_this_year = today.replace(day=31, month=12)
            first_day_of_next_year = last_day_of_this_year + datetime.timedelta(days=1)
            first_day_of_next_year_begining = datetime.datetime.combine(first_day_of_next_year, datetime.time())

            payments = payments.filter(date__gte=first_day_of_this_year_begining, date__lt=first_day_of_next_year_begining)

        elif date == "LastYear":
            first_day_of_next_year = today.replace(day=1, month=1, year=today.year - 1)
            first_day_of_next_year_begining = datetime.datetime.combine(first_day_of_next_year, datetime.time())

            first_day_of_this_year = today.replace(day=1, month=1)
            first_day_of_this_year_begining = datetime.datetime.combine(first_day_of_this_year, datetime.time())

            payments = payments.filter(date__gte=first_day_of_next_year_begining, date__lt=first_day_of_this_year_begining)

        return payments.order_by("-date")

    def list(self, request):
        payments = self._get_filtred_payments(request)

        # Extract non skiped payments and count

        not_skiped_payments = payments.exclude(status="Skiped")

        payments_total_amount_excluding_skiped = not_skiped_payments.aggregate(Sum('amount'))['amount__sum']
        payments_average_amount_excluding_skiped = not_skiped_payments.aggregate(Avg('amount'))['amount__avg']
        amount_donated = not_skiped_payments.aggregate(Sum('amount_donated'))['amount__sum']
        amount_for_owner = payments_total_amount_excluding_skiped - amount_donated

        if (amountAvg ): amountAvg = round(amountAvg,2)
        if (amountSum is None ): amountSum = 0
        if (amountAvg is None): amountAvg = 0.0

        # Count total payments

        total_payment_count = payments.count()

        # Paginate
        
        page = self.request.query_params.get("page", None)
        if page:
            paginator = Paginator(payments, 10) # 10 payments per page
            payments = paginator.get_page(page)

        # Serialize filtred payments

        serializer_class = None
        user: User = request.user
        
        if user.is_staff or (user.is_customer_user() and user.get_customer().can_see_donators):
            serializer_class = self._PaymentWithDonatorSerializer
        else:
            serializer_class = self._PaymentWithoutDonatorSerializer

        serializer = serializer_class(payments, many=True)

        return Response(
            {
                'payments': serializer.data,
                'amount_sum': amountSum,
                'amount_avg': amountAvg,
                'total_number_of_payments': total_payment_count,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'])
    def to_csv(self, request):
        payments = self._get_filtred_payments(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        writer = csv.DictWriter(response, fieldnames=['Id', 'Date',  'Transaction', 'Email donateur', 'Accord newsletter', 'Accord asso', 'Campagne', 'Terminal', 'Client', 'TPE', 'Montant en €','Jeu', 'Formule de dons'])
        writer.writeheader()

        for payment in payments.all():
            writer.writerow(
                {
                    'Id': payment.id, 
                    'Date': payment.date.strftime("%m/%d/%Y, %H:%M:%S"),
                    'Transaction': payment.status,
                    'Email donateur': payment.donator.email if payment.donator and payment.donator.email else ' ',
                    'Accord newsletter': "Oui" if payment.donator and payment.donator.accept_newsletter and payment.donator.accept_newsletter == True else "Non" if payment.donator and payment.donator.accept_newsletter and payment.donator.accept_newsletter == False else " " ,
                    'Accord asso': "Oui" if payment.donator and payment.donator.accept_asso and payment.donator.accept_asso == True else "Non" if payment.donator and payment.donator.accept_asso and payment.donator.accept_asso == False else " " ,
                    'Campagne': payment.campaign.name,
                    'Terminal': payment.terminal.name,
                    'Client': payment.terminal.customer.company,
                    'TPE': payment.terminal.payment_terminal,
                    'Montant en €': payment.amount,
                    'Jeu': payment.game.name if payment.game else "",
                    'Formule de dons': payment.donation_formula if payment.donation_formula else ""
                }
            )
        return response



class TerminalByOwner(APIView):
    # TODO protect
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal_serializer = LightTerminalSerializer(terminal)
            campaigns_serializer = CampaignSerializer(terminal.campaigns.order_by("-featured", "name"), many=True, context={"request": request})
            games_serializer = GameSerializer(terminal.games.order_by("-featured", "name"), many=True, context={"request": request})
            return Response(
                {
                    'terminal': terminal_serializer.data,
                    'campaigns': campaigns_serializer.data,
                    'games': games_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TurnOnTerminal(APIView):
    # TODO protect
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal.is_on = True
            terminal.save()
            serializer = LightTerminalSerializer(terminal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TurnOffTerminal(APIView):
    # TODO protect
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal.is_on = False
            terminal.is_playing = False
            terminal.save()
            serializer = LightTerminalSerializer(terminal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PlayingOnTerminal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal.is_playing = True
            terminal.save()
            serializer = LightTerminalSerializer(terminal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PlayingOffTerminal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal.is_playing = False
            terminal.save()
            serializer = LightTerminalSerializer(terminal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# Donator Model
class DonatorViewSet(viewsets.ModelViewSet):
    serializer_class = DonatorSerializer
    queryset = Donator.objects.all()
    permission_classes = [IsAuthenticated]


class DonatorByEmail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, email, format=None):
        try:
            donator = Donator.objects.get(email=email)
            serializer = DonatorSerializer(donator)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# Session Model
class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()
    permission_classes = [IsAuthenticated]


class AvgSessionByTerminal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, terminal, format=None):
        try:
            avg = Session.objects.filter(terminal=terminal).aggregate(Avg('timesession'))['timesession__avg'].seconds
            hours, remainder = divmod(avg, 3600)
            minutes, seconds = divmod(remainder, 60)
            string = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
            serializer = json.dumps(string)
            return Response(serializer, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

# Payment Model
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

    def paymentLog(self, paymentSerializer):
        # file : ${settings.LOG_PATH}/${terminalName}/${%Y-%m}-payments.log
        terminalName = LightTerminalSerializer(Terminal.objects.get(pk=paymentSerializer.data.get("terminal"))).data.get("name")
        filePath = os.path.join(settings.LOG_PATH, terminalName)
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        fileName = filePath + "/" + datetime.datetime.now().strftime("%Y-%m") +'-payments.log'
        logLine = str(datetime.datetime.now()) + " - [PAYMENT] - " + str(paymentSerializer.data)+"\n"
        
        log_file = open(fileName, "a")
        log_file.write(logLine)
        log_file.close();

    def paymentLogException(self, exception, paymentSerializer, request):
        if paymentSerializer.data.get("terminal") :
            # file : ${settings.LOG_PATH}/${terminalName}/${%Y-%m}-payments.log
            terminalName = LightTerminalSerializer(Terminal.objects.get(pk=paymentSerializer.data.get("terminal"))).data.get("name")
            filePath = os.path.join(settings.LOG_PATH, terminalName)
            if not os.path.exists(filePath):
                os.makedirs(filePath)
            fileName = filePath + "/" + datetime.datetime.now().strftime("%Y-%m") +'-payments.log'
            logLine = str(datetime.datetime.now()) + " - [ERROR] - " + str(exception) + "\n"
        else :
            fileName = settings.LOG_PATH + 'error-payments.log'
            logLine = str(datetime.datetime.now()) + " - [ERROR] - Unknown terminal ID\n"

        logLine += "[REQUEST] - " + str(request) + "\n"

        log_file = open(fileName, "a")
        log_file.write(logLine)
        log_file.close();

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try :
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            self.paymentLog(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            self.paymentLogException(sys.exc_info(), serializer, request.data)
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StatsByTerminal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, terminal, format=None):
        try:
            payment = Payment.objects.filter(terminal=terminal, status="Accepted").order_by('date')[:5]
            avg = Payment.objects.filter(terminal=terminal, status="Accepted").aggregate(Avg('amount'))
            avg_ts = Session.objects.filter(terminal=terminal).aggregate(Avg('timesession_global'))['timesession_global__avg']
            avg_game_ts = Session.objects.filter(terminal=terminal).aggregate(Avg('timesession'))['timesession__avg']
            ts_string = ''
            ts_game_string = ''
            if avg_ts:
                avg_ts = avg_ts.seconds
                hours, remainder = divmod(avg_ts, 3600)
                minutes, seconds = divmod(remainder, 60)
                ts_string = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
            if avg_game_ts:
                avg_game_ts = avg_game_ts.seconds
                hours, remainder = divmod(avg_game_ts, 3600)
                minutes, seconds = divmod(remainder, 60)
                ts_game_string = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
            serializer = {
                'avg_amount': avg['amount__avg'] or 0,
                'payments': PaymentFullSerializer(payment, many=True).data,
                'avg_ts': ts_string,
                'avg_game_ts': ts_game_string
            }
            serializer = json.dumps(serializer)
            return Response(serializer, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
