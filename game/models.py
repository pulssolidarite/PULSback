from django.db import models

# Create your models here.
class CoreFile(models.Model):
    file = models.FileField(upload_to="games/cores/")
    date_added = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Fichier Core n° {}'.format(self.pk)


class BiosFile(models.Model):
    file = models.FileField(upload_to="games/bios/")
    date_added = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Fichier Bios n° {}'.format(self.pk)


class Core(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    file = models.OneToOneField(CoreFile, on_delete=models.CASCADE)
    bios_path = models.CharField(max_length=255, null=True, blank=True, default=None)
    bios = models.OneToOneField(BiosFile, on_delete=models.CASCADE, null=True, blank=True, default=None)
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
    file = models.OneToOneField(GameFile, on_delete=models.CASCADE, related_name="rom")
    core = models.ForeignKey(Core, on_delete=models.SET_NULL, null=True, blank=True, related_name="games")
    description = models.TextField()
    is_video = models.BooleanField(default=False)
    video = models.CharField(max_length=255, null=True, blank=True)
    logo = models.FileField(blank=True, null=True, upload_to="games/logos/")
    is_archived = models.BooleanField(default=False)
    j_up = models.CharField(max_length=255, default="Haut", null=True, blank=True)
    j_down = models.CharField(max_length=255, default="Bas", null=True, blank=True)
    j_right = models.CharField(max_length=255, default="Droite", null=True, blank=True)
    j_left = models.CharField(max_length=255, default="Gauche", null=True, blank=True)
    btn_x = models.CharField(max_length=255, default="Rien", null=True, blank=True)
    btn_y = models.CharField(max_length=255, default="Rien", null=True, blank=True)
    btn_a = models.CharField(max_length=255, default="Rien", null=True, blank=True)
    btn_b = models.CharField(max_length=255, default="Rien", null=True, blank=True)
    btn_l = models.CharField(max_length=255, default="Rien", null=True, blank=True)
    btn_r = models.CharField(max_length=255, default="Rien", null=True, blank=True)
    btn_start = models.CharField(max_length=255, default="Start", null=True, blank=True)
    btn_select = models.CharField(max_length=255, default="Select", null=True, blank=True)
    type = models.CharField(max_length=255, default="Unique", null=True, blank=True)
    nb_players = models.IntegerField(default=1, null=True, blank=True)

    @property
    def nb_terminals(self):
        return self.terminals.count()

    def __str__(self):
        return self.name