from django.views.generic.list import ListView
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.views import APIView
from .models import Terminal, Donator, Session, Payment,Campaign
from game.models import Game, Core, GameFile, CoreFile
from fleet.models import Customer,User
from fleet.serializers import CustomerSerializer
from .serializers import *
from fleet.serializers import CampaignSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404
import json
from datetime import timedelta
import csv
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from tempfile import NamedTemporaryFile
import logging
from django.conf import settings
import os
from datetime import datetime
import sys
from backend.permissions import IsAdminOrCustomerUser
from django.core.exceptions import PermissionDenied

# Terminal Model
class TerminalViewSet(viewsets.ModelViewSet):
    """
    This view is used from SETH front admin or customer
    """

    queryset = Terminal.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated, IsAdminOrCustomerUser] # Only accessible for admin or customer users
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
            terminals = Terminal.objects.filter(is_on=True, owner__customer=user.get_customer())
            terminals = TerminalSemiSerializer(terminals, many=True, context={"request": request})
            collected = Payment.objects.filter(terminal__owner__customer=user.get_customer(), date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
            collected_last = Payment.objects.filter(terminal__owner__customer=user.get_customer(), date__month=datetime.datetime.now().month - 1, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
            nb_donators = Session.objects.filter(terminal__owner__customer=user.get_customer(), start_time__month=datetime.datetime.now().month, start_time__year=datetime.datetime.now().year).count()
            nb_donators_last = Session.objects.filter(terminal__owner__customer=user.get_customer(), start_time__month=datetime.datetime.now().month - 1, start_time__year=datetime.datetime.now().year).count()
            nb_terminals = Terminal.objects.filter(owner__customer=user.get_customer()).count()
            total_gamesession = Session.objects.filter(terminal__owner__customer=user.get_customer()).aggregate(Sum('timesession'))['timesession__sum']
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
            terminals = Terminal.objects.filter(owner__customer=user.get_customer())
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
            campaign = self.request.query_params.get('campaign')
            terminal = self.request.query_params.get('terminal_id')
            client = self.request.query_params.get('client_id')
            formule = self.request.query_params.get('formule_')
            transaction = self.request.query_params.get('transaction_id')
            game = self.request.query_params.get('game_id')
            tpe = self.request.query_params.get('tpe')
            date = self.request.query_params.get('date')
            date_start = self.request.query_params.get('date_start')
            date_end = self.request.query_params.get('date_end')
            try :
                results_number = int( self.request.query_params.get('results_number'))
            except ValueError :
                try :
                    results_number = float(self.request.query_params.get('results_number'))
                    results_number = int(results_number)
                except ValueError :
                    results_number = 50
            url_parameters = self.request.query_params.dict().copy()
            for key, value in self.request.query_params.items():
                if ( value in [ 'all', ' ','','DD-MM-YYYY H:m:s', 'DD-MM-YYYY'] or key == 'results_number'):
                    url_parameters.pop(key)
            if ( "client_id" in url_parameters) :
                if ( terminal !=  "all" ) :
                    users_cl = User.objects.filter(customer_id=client)
                    owned_terminals = Terminal.objects.filter(owner_id__in=users_cl.values_list('id', flat=True))
                    l1=set(owned_terminals.values_list('id', flat=True))
                    l2 = {int(url_parameters['terminal_id'])}
                    common_vals = l1.intersection(l2)
                    url_parameters.pop('terminal_id')
                    url_parameters['terminal_id__in'] = common_vals
                else :
                    users_cl = User.objects.filter(customer_id=client)
                    owned_terminals = Terminal.objects.filter(owner_id__in=users_cl.values_list('id', flat=True))
                    url_parameters['terminal_id__in'] =  owned_terminals.values_list('id', flat=True)
                url_parameters.pop('client_id')
            if ('date_start' in url_parameters) :
               print (url_parameters['date_start'])
               val = url_parameters['date_start'].replace('T', ' ')
               converted_date_start =  datetime.datetime.strptime(val, '%d-%m-%Y %H:%M:%S')
               url_parameters.pop('date_start')
               url_parameters['date__gte'] = converted_date_start
            if ( 'date_end' in url_parameters):
                val = url_parameters['date_end'].replace('T', ' ')
                converted_date_end = datetime.datetime.strptime(val , '%d-%m-%Y %H:%M:%S')
                url_parameters.pop('date_end')
                url_parameters['date__lt'] = converted_date_end
            if ( "date" in url_parameters):
                if ( 'date__lt' in url_parameters):
                    url_parameters.pop('date__lt')
                if ('date__gte' in url_parameters) :
                    url_parameters.pop('date__gte')
                if ( date =="Today" ) :
                    now = datetime.datetime.now()
                    today = datetime.datetime(now.year, now.month, now.day)
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = today.date()
                    url_parameters['date__lt'] = today.date() + timedelta(days=1)
                elif (  date =="Yesterday") :
                    now = datetime.datetime.now()
                    today = datetime.datetime(now.year, now.month, now.day)
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = today.date() - timedelta(days=1)
                    url_parameters['date__lt'] = today.date()
                elif (date == "7days"):
                    some_day_last_week = datetime.datetime.now().date() - timedelta(days=7)
                    monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
                    monday_of_this_week = monday_of_last_week + timedelta(days=7)
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = some_day_last_week
                    url_parameters['date__lt'] = datetime.datetime.now().date() + timedelta(days=1)
                elif (date == "CurrentWeek"):
                    today = datetime.datetime.now()
                    monday_of_this_week = today.date() - timedelta(days=today.weekday())
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = monday_of_this_week
                    url_parameters['date__lt'] = monday_of_this_week + timedelta(days=7)
                elif (date == "LastWeek"):
                    some_day_last_week = datetime.datetime.now().date() - timedelta(days=7)
                    monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
                    monday_of_this_week = monday_of_last_week + timedelta(days=7)
                    print (monday_of_last_week)
                    print (monday_of_this_week)
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = monday_of_last_week
                    url_parameters['date__lt'] = monday_of_this_week
                elif (date == "CurrentMonth"):
                    now = datetime.datetime.now()
                    start_month = datetime.datetime(now.year, now.month, 1)
                    date_on_next_month = start_month + datetime.timedelta(35)
                    start_next_month = datetime.datetime(date_on_next_month.year, date_on_next_month.month, 1)
                    last_day_month = start_next_month - datetime.timedelta(1)
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = start_month.date()
                    url_parameters['date__lt'] = last_day_month.date()
                elif (date == "LastMonth"):
                    today = datetime.date.today()
                    first = today.replace(day=1)  # first date of current month
                    end_previous_month = first - datetime.timedelta(days=1)
                    start_previous_month = end_previous_month.replace(day=1)
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = start_previous_month
                    url_parameters['date__lt'] = end_previous_month
                elif (date == "ThisYear"):
                    now = datetime.datetime.now()
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = now.date().replace(day=1, month=1)
                    url_parameters['date__lt'] = now.date().replace(day=31, month=12)
                else :
                    now = datetime.datetime.now()
                    url_parameters.pop('date')
                    url_parameters['date__gte'] = now.date().replace(day=1, month=1, year=now.year - 1)
                    url_parameters['date__lt'] = now.date().replace(day=31, month=12, year=now.year - 1)
            if ('donation_formula' in url_parameters and  'payment_terminal' in url_parameters):
                url_parameters.pop('donation_formula')
                url_parameters.pop('payment_terminal')
                donation_formula = self.request.query_params.get('donation_formula')
                tpe = self.request.query_params.get('payment_terminal')
                terminals = Terminal.objects.filter(donation_formula=donation_formula,payment_terminal=tpe )
                res_objects = Payment.objects.filter(**url_parameters).filter(terminal_id__in=terminals)
                TotalResults = Payment.objects.filter(**url_parameters).filter(terminal_id__in=terminals)
            elif ('donation_formula'  in url_parameters):
                url_parameters.pop('donation_formula')
                donation_formula = self.request.query_params.get('donation_formula')
                terminals = Terminal.objects.filter(donation_formula=donation_formula)
                res_objects = Payment.objects.filter(**url_parameters).filter(terminal_id__in=terminals)
                TotalResults = Payment.objects.filter(**url_parameters).filter(terminal_id__in=terminals)
            elif   ('payment_terminal'  in url_parameters):
                url_parameters.pop('payment_terminal')
                tpe = self.request.query_params.get('payment_terminal')
                terminals = Terminal.objects.filter( payment_terminal=tpe)
                res_objects = Payment.objects.filter(**url_parameters).filter(terminal_id__in=terminals)
                TotalResults = Payment.objects.filter(**url_parameters).filter(terminal_id__in=terminals)
            else :
                res_objects = Payment.objects.filter(**url_parameters)
                TotalResults = Payment.objects.filter(**url_parameters)

            res_objects_excluded = res_objects.exclude(status="Skiped").order_by('-date')[:results_number]
            res_objects = res_objects.order_by('-date')[:results_number]
            TotalResults = TotalResults.order_by('-date').count()
            res = PaymentFullSerializer(res_objects, many=True, context={"request": request})
            amountSum = res_objects_excluded.aggregate(Sum('amount'))['amount__sum']
            amountAvg =  res_objects_excluded.aggregate(Avg('amount'))['amount__avg']
            if (amountAvg ): amountAvg = round(amountAvg,2)
            if (amountSum is None ): amountSum = 0
            if (amountAvg is None): amountAvg = 0.0
            total_games = res_objects.count()
            return Response({ 'payments' :  res.data, 'amountSum': amountSum, 'amountAvg': amountAvg , 'total_games': total_games, 'TotalResults' : TotalResults}, status=status.HTTP_200_OK)


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
        fileName = filePath + "/" + datetime.now().strftime("%Y-%m") +'-payments.log'
        logLine = str(datetime.now()) + " - [PAYMENT] - " + str(paymentSerializer.data)+"\n"
        
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
            fileName = filePath + "/" + datetime.now().strftime("%Y-%m") +'-payments.log'
            logLine = str(datetime.now()) + " - [ERROR] - " + str(exception) + "\n"
        else :
            fileName = settings.LOG_PATH + 'error-payments.log'
            logLine = str(datetime.now()) + " - [ERROR] - Unknown terminal ID\n"

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
