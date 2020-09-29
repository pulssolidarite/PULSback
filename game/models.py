from django.db import models

# Create your models here.
class CoreFile(models.Model):
    file = models.FileField(upload_to="games/cores/")
    date_added = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Fichier Core n° {}'.format(self.pk)


class Core(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    file = models.OneToOneField(CoreFile, on_delete=models.CASCADE)
    description = models.TextField()
    
    def __str__(self):
        return self.name

    @property
    def nb_games(self):
        return self.games.count() or 0


class GameFile(models.Model):
    file = models.FileField(upload_to="games/roms/")
    date_added = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Fichier Rom n° {}'.format(self.pk)


class Game(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    file = models.OneToOneField(GameFile, on_delete=models.CASCADE)
    core = models.ForeignKey(Core, on_delete=models.CASCADE, related_name="games")
    description = models.TextField()
    logo = models.FileField(blank=True, null=True, upload_to="games/logos/")
    is_archived = models.BooleanField(default=False)

    @property
    def nb_terminals(self):
        return self.terminals.count()

    def __str__(self):
        return self.name