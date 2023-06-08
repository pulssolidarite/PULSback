from django.db import models


# Create your models here.
class CoreFile(models.Model):
    file = models.FileField(upload_to="games/cores/")
    date_added = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Fichier Core n° {}".format(self.pk)


class BiosFile(models.Model):
    file = models.FileField(upload_to="games/bios/")
    date_added = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Fichier Bios n° {}".format(self.pk)


class Core(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    file = models.OneToOneField(CoreFile, on_delete=models.CASCADE)
    bios_path = models.CharField(max_length=255, null=True, blank=True, default=None)
    bios = models.OneToOneField(
        BiosFile, on_delete=models.CASCADE, null=True, blank=True, default=None
    )
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
        return "Fichier Rom n° {}".format(self.pk)


class Game(models.Model):
    name = models.CharField(max_length=255, verbose_name="Titre")
    path = models.CharField(
        max_length=255, verbose_name="Nom du fichier rom ou répertoire du jeu sur Hera"
    )
    file = models.OneToOneField(
        GameFile,
        on_delete=models.CASCADE,
        related_name="rom",
        verbose_name="Fichier rom ou fichier d'installation",
    )
    core = models.ForeignKey(
        Core,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="games",
        verbose_name="Fichier core",
    )
    description = models.TextField(verbose_name="Description")
    is_video = models.BooleanField(default=False)
    video = models.CharField(max_length=255, null=True, blank=True)
    logo = models.FileField(blank=True, null=True, upload_to="games/logos/")
    cover = models.FileField(blank=True, null=True, upload_to="games/covers/")
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
    btn_select = models.CharField(
        max_length=255, default="Select", null=True, blank=True
    )
    type = models.CharField(max_length=255, default="Unique", null=True, blank=True)
    nb_players = models.IntegerField(default=1, null=True, blank=True)
    featured = models.BooleanField(verbose_name="Jeux du moment", default=False)
    installation_script = models.TextField(
        null=True, blank=True, verbose_name="Script d'installation"
    )
    execution_script = models.TextField(
        null=True, blank=True, verbose_name="Script de lancement"
    )

    def save(self, *args, **kwargs):
        """
        Make sure only one Game object has featured == True
        """
        if self.featured:
            try:
                old_featured = Game.objects.get(featured=True)
                if old_featured and self != old_featured:
                    old_featured.featured = False
                    old_featured.save()
            except Game.DoesNotExist:
                pass

        super(Game, self).save(*args, **kwargs)

    @property
    def nb_terminals(self):
        return self.terminals.count()

    def __str__(self):
        return self.name
