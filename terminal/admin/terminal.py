from django.contrib import admin

from terminal.models import Terminal


@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    # List view

    list_display = (
        "name",
        "owner",
        "customer",
        "is_active",
        "is_on",
        "is_playing",
        "is_archived",
        "donation_formula",
        "version",
        "check_for_updates",
        "restart",
        "_restart_every_day",
    )

    def _restart_every_day(self, obj):
        if obj.restart_every_day_from and obj.restart_every_day_until:
            return f"Entre {obj.restart_every_day_from} et {obj.restart_every_day_until} UTC"
        return None

    actions = [
        "_request_check_for_updates",
    ]

    def _request_check_for_updates(self, request, queryset):
        for terminal in queryset:
            terminal.check_for_updates = True
            terminal.save()

    _request_check_for_updates.short_description = "Forcer MAJ Hera"

    list_filter = (
        "name",
        "owner",
        "customer",
        "donation_formula",
    )

    search_fields = ("customer",)

    ordering = ("customer",)

    # Form view

    readonly_fields = ("last_restarted",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "customer",
                    "location",
                ),
            },
        ),
        (
            "Compte de connexion",
            {
                "fields": ("owner",),
            },
        ),
        (
            "Etat",
            {
                "fields": (
                    "is_active",
                    "is_on",
                    "is_playing",
                    "is_archived",
                ),
            },
        ),
        (
            "TPE",
            {
                "fields": (
                    "payment_terminal",
                    "payment_terminal_type",
                ),
            },
        ),
        (
            "Paramétrage général",
            {
                "fields": (
                    "play_timer",
                    "free_mode_text",
                ),
            },
        ),
        (
            "Donations",
            {
                "fields": (
                    "donation_formula",
                    "donation_share",
                    "donation_min_amount",
                    "donation_default_amount",
                    "donation_max_amount",
                ),
            },
        ),
        (
            "Contenu",
            {
                "fields": (
                    (
                        "campaigns",
                        "games",
                    ),
                )
            },
        ),
        (
            "Redémarrages",
            {
                "fields": (
                    "restart",
                    "restart_every_day_from",
                    "restart_every_day_until",
                    "last_restarted",
                )
            },
        ),
    )
