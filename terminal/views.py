from django.views.generic.list import ListView
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.views import APIView
from .models import Terminal, Donator, Session, Payment
from game.models import Game, Core, GameFile, CoreFile
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
import logging
from django.conf import settings
import os
from datetime import datetime
import sys

# Terminal Model
class TerminalViewSet(viewsets.ModelViewSet):
    queryset = Terminal.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated]
    serializer_class = TerminalSerializer

    def retrieve(self, request, *args, **kwargs):
        queryset = get_object_or_404(Terminal, pk=kwargs["pk"])
        serializer = TerminalFullSerializer(queryset, many=False)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = Terminal.objects.filter(is_archived=False)
        serializer = TerminalSemiSerializer(queryset, many=True, read_only=True)
        return Response(serializer.data)


class CampaignsByTerminal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            campaigns = Terminal.objects.get(pk=pk).campaigns
            campaigns = CampaignSerializer(campaigns, many=True, context={"request": request})
            return Response(campaigns.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class DashboardStats(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        terminals = Terminal.objects.filter(is_on=True)
        terminals = TerminalSemiSerializer(terminals, many=True, context={"request": request})
        collected = Payment.objects.filter(date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
        collected_last = Payment.objects.filter(date__month=datetime.datetime.now().month - 1, date__year=datetime.datetime.now().year).aggregate(Sum('amount'))['amount__sum']
        nb_donators = Session.objects.filter(start_time__month=datetime.datetime.now().month, start_time__year=datetime.datetime.now().year).count()
        nb_donators_last = Session.objects.filter(start_time__month=datetime.datetime.now().month - 1, start_time__year=datetime.datetime.now().year).count()
        nb_terminals = Terminal.objects.all().count()
        total_gamesession = Session.objects.all().aggregate(Sum('timesession'))['timesession__sum']
        return Response({'terminals': terminals.data, 'collected': collected, 'nb_donators': nb_donators, 'nb_terminals': nb_terminals, 'total_gamesession': total_gamesession, 'collected_last': collected_last, 'nb_donators_last': nb_donators_last}, status=status.HTTP_200_OK)



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
