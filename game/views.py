from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework.decorators import action

from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import viewsets
from .forms import *

from fleet.models import User
from backend.permissions import IsAdminOrCustomerUser


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()

    def get_serializer_class(self):
        user: User = self.request.user

        if user.is_staff:
            return GameSerializer # Return extended serializer only for admin
        
        return GameLightSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve" "featured", "not_featured"]:
            permission_classes = [IsAuthenticated, IsAdminOrCustomerUser]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset().filter(is_archived=False).order_by("-featured", "name"), many=True, read_only=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        game = get_object_or_404(self.get_queryset(), pk=pk)
        game.is_archived = True
        game.terminals.clear()
        game.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        if not request.FILES['file']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        form = GameFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            return Response(GameFileSerializer(file).data, status=status.HTTP_201_CREATED)
        else:
            print(form.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def featured(self, request, pk, format=None):
        user: User = request.user
        game = get_object_or_404(self.get_queryset(), pk=pk)

        if user.is_staff:
            game.featured = True
            game.save()

        else:
            customer = user.get_customer()
            customer.featured_game = game
            customer.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def not_featured(self, request, pk, format=None):
        user: User = request.user
        game = get_object_or_404(self.get_queryset(), pk=pk)

        if user.is_staff:
            game.featured = False
            game.save()

        else:
            customer = user.get_customer()
            if customer.featured_game == game:
                customer.featured_game = None
                customer.save()

        return Response(status=status.HTTP_200_OK)




# Core Model
class CoreListView(ListAPIView):
    serializer_class = CoreSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated, IsAdminUser] # Only admin

class CoreCreateView(CreateAPIView):
    serializer_class = CoreLightSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated, IsAdminUser] # Only admin

class CoreRetrieveDestroyView(RetrieveDestroyAPIView):
    serializer_class = CoreSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated, IsAdminUser] # Only admin

class CoreUpdateView(UpdateAPIView):
    serializer_class = CoreLightSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated, IsAdminUser] # Only admin
    

class CoreFileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsAdminUser] # Only admin

    def post(self, request, format=None):
        if request.FILES['file']:
            form = CoreFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save()
                return Response(CoreFileSerializer(file).data, status=status.HTTP_201_CREATED)
            else:
                print(form.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)


class BiosFileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsAdminUser] # Only admin

    def post(self, request, format=None):
        if request.FILES['file']:
            form = BiosFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save()
                return Response(BiosFileSerializer(file).data, status=status.HTTP_201_CREATED)
            else:
                print(form.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)