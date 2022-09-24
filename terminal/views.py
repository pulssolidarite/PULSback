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

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView

from game.models import Game

from fleet.models import Customer, User
from fleet.serializers import CustomerSerializer, CampaignSerializer

from backend.permissions import IsAdminOrCustomerUser, NormalUserListRetrieveOnly

from .models import Terminal, Donator, Session, Payment,Campaign
from .serializers import *


# Terminal Model
class TerminalViewSet(viewsets.ModelViewSet):
    """
    This view is used from SETH front admin or customer
    """

    queryset = Terminal.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser, NormalUserListRetrieveOnly]
    serializer_class = TerminalSerializer

    def get_queryset(self):
        user: User = self.request.user

        if user.is_customer_user():
            return Terminal.objects.filter(is_archived=False, customer=user.get_customer()) # For customer, return all terminals that belong to this customer

        elif user.is_staff:
            return Terminal.objects.filter(is_archived=False)

        else:
            raise PermissionDenied()

    def retrieve(self, request, *args, **kwargs):
        queryset = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        serializer = TerminalFullSerializer(queryset, many=False)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        serializer = TerminalSemiSerializer(self.get_queryset(), many=True, read_only=True)
        return Response(serializer.data)


class CampaignsByTerminal(APIView):
    """
    This view is used from SETH front admin or customer
    """

    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser] # Only accessible for admin or customer users

    def get_queryset(self):
        user: User = self.request.user

        if user.is_customer_user():
            return Terminal.objects.filter(is_archived=False, customer=user.get_customer()) # For customer, return all terminals that belong to this customer

        elif user.is_staff:
            return Terminal.objects.filter(is_archived=False)

        else:
            raise PermissionDenied()

    def get(self, request, pk, format=None):
        terminal = get_object_or_404(self.get_queryset(), pk=pk)
        campaigns = terminal.campains
        serializer = CampaignSerializer(campaigns, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
        


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
            nb_donators = Session.objects.filter(terminal__customer=user.get_customer(), start_time__month=datetime.datetime.now().month, start_time__year=datetime.datetime.now().year).count()
            nb_donators_last = Session.objects.filter(terminal__customer=user.get_customer(), start_time__month=datetime.datetime.now().month - 1, start_time__year=datetime.datetime.now().year).count()
            nb_terminals = Terminal.objects.filter(customer=user.get_customer()).count()
            total_gamesession = Session.objects.filter(terminal__customer=user.get_customer()).aggregate(Sum('timesession'))['timesession__sum']
            return Response({'terminals': terminals.data, 'campaigns': campaigns_serlializer.data, 'collected': collected, 'nb_donators': nb_donators, 'nb_terminals': nb_terminals, 'total_gamesession': total_gamesession, 'collected_last': collected_last, 'nb_donators_last': nb_donators_last}, status=status.HTTP_200_OK)

        elif user.is_staff:
            terminals = Terminal.objects.filter(is_on=True)
            terminals = TerminalSemiSerializer(terminals, many=True, context={"request": request})

            collected = Payment.objects.filter(date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
            collected_last = Payment.objects.filter(date__month=datetime.datetime.now().month - 1, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
            nb_donators = Session.objects.filter(start_time__month=datetime.datetime.now().month, start_time__year=datetime.datetime.now().year).count()
            nb_donators_last = Session.objects.filter(start_time__month=datetime.datetime.now().month - 1, start_time__year=datetime.datetime.now().year).count()
            nb_terminals = Terminal.objects.all().count()
            total_gamesession = Session.objects.all().aggregate(Sum('timesession'))['timesession__sum']
            return Response({'terminals': terminals.data, 'campaigns': campaigns_serlializer.data, 'collected': collected, 'nb_donators': nb_donators, 'nb_terminals': nb_terminals, 'total_gamesession': total_gamesession, 'collected_last': collected_last, 'nb_donators_last': nb_donators_last}, status=status.HTTP_200_OK)

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

class PaymentFiltered(APIView):
    """
    This view is used from SETH front admin or customer
    """
    # TODO filter by user

    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser] # Only accessible for admin or customer users

    def get(self, request, format=None):
        """
        Possible query params :
        - campaign_id
        - terminal_id
        - client_id
        - status
        - game_id
        - date
        - date_start
        - date_end
        - results_number
        - payment_terminal
        - donation_formula
        """

        # Fetch params
        
        campaign_id = self.request.query_params.get('campaign_id')
        terminal_id = self.request.query_params.get('terminal_id')
        client_id = self.request.query_params.get('client_id')
        donation_formula = self.request.query_params.get('donation_formula')
        status = self.request.query_params.get('status')
        game_id = self.request.query_params.get('game_id')
        date = self.request.query_params.get('date')
        date_start = self.request.query_params.get('date_start')
        date_end = self.request.query_params.get('date_end')
        payment_terminal = self.request.query_params.get('payment_terminal')
        results_number = self.request.query_params.get('results_number')

        # Parse results_number
        
        if results_number:
            results_number = int(results_number)
        else:
            results_number = 50

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

        if terminal_id and terminal_id not in ["all", "", " "]:
            payments = payments.filter(terminal=terminal_id)

        # Filter by customer

        if client_id and client_id not in ["all", "", " "]:
            payments = payments.filter(terminal__customer_id=client_id)

        # Filter by campaign

        if campaign_id and campaign_id not in ["all", "", " "]:
            payments = payments.filter(campaign_id=campaign_id)

        # Filter by game

        if game_id and campaign_id not in ["all", "", " "]:
            payments = payments.filter(game_id=game_id)

        # Filter by status

        if status and status not in ["all", "", " "]:
            payments = payments.filter(status=status)

        # Filter by donation_formula

        # TODO

        # Filter by payment_terminal

        # TODO

        # Filter by date_start

        if date_start and date_start not in ['DD-MM-YYYY H:m:s', 'DD-MM-YYYY', "", " "]:
            formatted_date = date_start.replace('T', ' ')
            converted_date_start =  datetime.datetime.strptime(formatted_date, '%d-%m-%Y %H:%M:%S')
            payments = payments.filter(date__gte=converted_date_start)

        # Filter by date_end

        if date_end and date_end not in ['DD-MM-YYYY H:m:s', 'DD-MM-YYYY', "", " "]:
            formatted_date = date_end.replace('T', ' ')
            converted_date_end =  datetime.datetime.strptime(formatted_date, '%d-%m-%Y %H:%M:%S')
            payments = payments.filter(date__lt=converted_date_end)

        # Filter by date (period)

        if date is "Today":
            today = datetime.datetime.now().date()
            tomorrow = today + datetime.timedelta(1)
            today_start = datetime.datetime.combine(today, datetime.time())
            today_end = datetime.datetime.combine(tomorrow, datetime.time())

            payments = payments.filter(date__gte=today_start, date_lt=today_end)

        elif date is "Yesterday":
            today = datetime.datetime.now().date()
            tomorrow = today + datetime.timedelta(1)
            after_tomorrow = tomorrow + datetime.timedelta(1)
            tomorrow_start = datetime.datetime.combine(tomorrow, datetime.time())
            tomorrow_end = datetime.datetime.combine(after_tomorrow, datetime.time())

            payments = payments.filter(date__gte=tomorrow_start, date_lt=tomorrow_end)

        elif date is "7days":
            today = datetime.datetime.now().date()
            today_start = datetime.datetime.combine(today, datetime.time())

            in_8_days = today + datetime.timedelta(8)
            in_7_days_end = datetime.datetime.combine(in_8_days, datetime.time())

            payments = payments.filter(date__gte=today_start, date_lt=in_7_days_end)

        elif date is "CurrentWeek":
            today = datetime.datetime.now().date()
            tomorrow = today + datetime.timedelta(1)
            today_end = datetime.datetime.combine(tomorrow, datetime.time())

            monday_of_this_week = today.date() - datetime.timedelta(days=today.weekday())
            monday_of_this_week_start = datetime.datetime.combine(monday_of_this_week, datetime.time())

            payments = payments.filter(date__gte=monday_of_this_week_start, date_lt=today_end)

        elif date is "LastWeek":
            some_day_last_week = datetime.now().date() - datetime.timedelta(days=7)
            monday_of_last_week = some_day_last_week - datetime.timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
            monday_of_last_week_start = datetime.datetime.combine(monday_of_last_week, datetime.time())
            
            monday_of_this_week = today.date() - datetime.timedelta(days=today.weekday())
            monday_of_this_week_start = datetime.datetime.combine(monday_of_this_week, datetime.time())

            payments = payments.filter(date__gte=monday_of_last_week_start, date_lt=monday_of_this_week_start)

        elif date is "CurrentMonth":
            now = datetime.datetime.now()
            start_month = datetime.datetime(now.year, now.month, 1)
            date_on_next_month = start_month + datetime.datetime.timedelta(35)
            start_next_month = datetime.datetime(date_on_next_month.year, date_on_next_month.month, 1)

            payments = payments.filter(date__gte=start_month, date_lt=start_next_month)

        elif date is "LastMonth":
            today = datetime.datetime.date.today()
            first = today.replace(day=1)  # first date of current month
            end_previous_month = first - datetime.datetime.timedelta(days=1)
            start_previous_month = end_previous_month.replace(day=1)

            now = datetime.datetime.now()
            start_this_month = datetime.datetime(now.year, now.month, 1)

            payments = payments.filter(date__gte=start_previous_month, date_lt=start_this_month)

        elif date is "ThisYear":
            now = datetime.datetime.now()
            first_day_of_this_year = now.date().replace(day=1, month=1)
            first_day_of_this_year_begining = datetime.datetime.combine(first_day_of_this_year, datetime.time())

            last_day_of_this_year = now.date().replace(day=31, month=12)
            first_day_of_next_year = last_day_of_this_year + datetime.timedelta(days=1)
            first_day_of_next_year_begining = datetime.datetime.combine(first_day_of_next_year, datetime.time())

            payments = payments.filter(date__gte=first_day_of_this_year_begining, date_lt=first_day_of_next_year_begining)

        elif date is "LastYear":
            now = datetime.datetime.now()
            first_day_of_next_year = now.date().replace(day=1, month=1, year=now.year - 1)
            first_day_of_next_year_begining = datetime.datetime.combine(first_day_of_next_year, datetime.time())

            first_day_of_this_year = now.date().replace(day=1, month=1)
            first_day_of_this_year_begining = datetime.datetime.combine(first_day_of_this_year, datetime.time())

            payments = payments.filter(date__gte=first_day_of_next_year_begining, date_lt=first_day_of_this_year_begining)

        # Extract non skiped payments

        not_skiped_payments = payments.exclude(status="Skiped")

        # Count total payments

        total_payment_count = payments.count()

        # Order by date and extract x first ones

        payments = payments.order_by('-date')[:results_number]
        not_skiped_payments = not_skiped_payments.order_by('-date')[:results_number]

        # Count filtred results

        payment_count = payments.count()
        not_skiped_payment_count = not_skiped_payments.count()

        # Serialize filtred payments

        payments_serialized = PaymentFullSerializer(payments, many=True, context={"request": request})

        # Count amount

        amountSum = not_skiped_payment_count.aggregate(Sum('amount'))['amount__sum']
        amountAvg =  not_skiped_payment_count.aggregate(Avg('amount'))['amount__avg']

        if (amountAvg ): amountAvg = round(amountAvg,2)
        if (amountSum is None ): amountSum = 0
        if (amountAvg is None): amountAvg = 0.0
        
        return Response({ 'payments' :  payments_serialized.data, 'amountSum': amountSum, 'amountAvg': amountAvg , 'total_games': payment_count, 'TotalResults' : total_payment_count}, status=status.HTTP_200_OK)


class CSVviewSet(APIView):
    """
    This view is used from SETH front admin or customer
    """
    # TODO filter by user

    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser] # Only accessible for admin or customer users

    def get(self, request, format=None):
            res = PaymentFiltered.get(self, request)
            data = dict(res.data)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="export.csv"'
            writer = csv.DictWriter(response, fieldnames=['Id', 'Date',  'Transaction', 'Email donateur', 'Accord newsletter', 'Accord asso', 'Campagne', 'Terminal', 'Client', 'TPE', 'Montant en €','Jeu', 'Formule de dons'])
            writer.writeheader()
            for key in data['payments']:
                try:
                    writer.writerow(
                        {
                            'Id': key['id'], 
                            'Date': key['date'].replace('-','/'),
                            'Transaction': key['status'],
                            'Email donateur': key['donator']["email"] if key['donator']["email"] else ' ',
                            'Accord newsletter': "Oui" if key['donator']["accept_newsletter"] else "Non",
                            'Accord asso': "Oui" if key['donator']["accept_asso"] else "Non",
                            'Campagne': key['campaign']['name'],
                            'Terminal': key['terminal']['name'],
                            'Client': key['terminal']['customer']['company'],
                            'TPE': key['terminal']['payment_terminal'],
                            'Montant en €': key['amount'],
                            'Jeu': key['game']['name'],
                            'Formule de dons': key['terminal']['donation_formula'],
                        }
                    )
                except Exception as e:
                    print(e)
                    print("KEY", json.dumps(key))
            return response


class GamesByTerminal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            games = Terminal.objects.get(pk=pk).games
            games = GameSerializer(games, many=True, context={"request": request})
            return Response(games.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TerminalByOwner(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            serializer = TerminalSerializer(terminal)
            campaigns = CampaignSerializer(terminal.campaigns, many=True, context={"request": request})
            games = GameSerializer(terminal.games, many=True, context={"request": request})
            return Response({'terminal': serializer.data, 'campaigns': campaigns.data, 'games': games.data}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TurnOnTerminal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal.is_on = True
            terminal.save()
            serializer = TerminalSerializer(terminal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TurnOffTerminal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal.is_on = False
            terminal.is_playing = False
            terminal.save()
            serializer = TerminalSerializer(terminal)
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
            serializer = TerminalSerializer(terminal)
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
            serializer = TerminalSerializer(terminal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ActivateTerminal(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk, format=None):
        try:
            terminal = Terminal.objects.get(pk=pk)
            terminal.is_active = True
            terminal.owner.is_active = True
            terminal.save()
            terminal.owner.save()
            serializer = TerminalSerializer(terminal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class DeactivateTerminal(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk, format=None):
        try:
            terminal = Terminal.objects.get(pk=pk)
            terminal.is_active = False
            terminal.owner.is_active = False
            terminal.is_on = False
            terminal.is_playing = False
            terminal.save()
            terminal.owner.save()
            serializer = TerminalSerializer(terminal)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ArchiveTerminal(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk, format=None):
        try:
            terminal = Terminal.objects.get(pk=pk)
            terminal.is_active = False
            terminal.owner.is_active = False
            terminal.is_archived = True
            terminal.save()
            terminal.owner.save()
            serializer = TerminalSerializer(terminal)
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
        terminalName = TerminalSerializer(Terminal.objects.get(pk=paymentSerializer.data.get("terminal"))).data.get("name")
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
            terminalName = TerminalSerializer(Terminal.objects.get(pk=paymentSerializer.data.get("terminal"))).data.get("name")
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
