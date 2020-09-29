from rest_framework.generics import *
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import viewsets
from .forms import *


# Game Model
class GameListView(ListAPIView):
    serializer_class = GameSerializer
    queryset = Game.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated]

class GameCreateView(CreateAPIView):
    serializer_class = GameLightSerializer
    queryset = Game.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated]

class GameRetrieveDestroyView(RetrieveDestroyAPIView):
    serializer_class = GameSerializer
    queryset = Game.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Game, pk=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        game.is_archived = True
        game.terminals.clear()
        game.save()
        return Response(status=status.HTTP_200_OK)

class GameUpdateView(UpdateAPIView):
    serializer_class = GameLightSerializer
    queryset = Game.objects.filter(is_archived=False)
    permission_classes = [IsAuthenticated]

class GameFileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        if request.FILES['file']:
            form = GameFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save()
                return Response(GameFileSerializer(file).data, status=status.HTTP_201_CREATED)
            else:
                print(form.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)


# Core Model
class CoreListView(ListAPIView):
    serializer_class = CoreSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated]

class CoreCreateView(CreateAPIView):
    serializer_class = CoreLightSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated]

class CoreRetrieveDestroyView(RetrieveDestroyAPIView):
    serializer_class = CoreSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated]

class CoreUpdateView(UpdateAPIView):
    serializer_class = CoreLightSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated]
    

class CoreFileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        if request.FILES['file']:
            form = CoreFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save()
                return Response(CoreFileSerializer(file).data, status=status.HTTP_201_CREATED)
            else:
                print(form.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)