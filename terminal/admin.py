from django.contrib import admin

from .models import Donator, Payment, Session, Terminal

# Register your models here.
admin.site.register(Donator)
admin.site.register(Session)


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
        "_check_for_updates",
        "restart",
        "restart_every_day_from",
        "restart_every_day_until",
        "_should_restart_now",
    )

    def _check_for_updates(self, terminal):
        return terminal.check_for_updates

    _check_for_updates.short_description = "Vérification des mises à jours demandée"
    _check_for_updates.boolean = True

    actions = [
        "_request_check_for_updates",
    ]

    def _request_check_for_updates(self, request, queryset):
        for terminal in queryset:
            terminal.check_for_updates = True
            terminal.save()

    _request_check_for_updates.short_description = "Vérifier les mises à jours"

    def _should_restart_now(self, terminal):
        return terminal.should_restart

    _should_restart_now.short_description = "Doit redémarrer maintenant"

    list_filter = (
        "name",
        "owner",
        "customer",
        "donation_formula",
    )

    search_fields = ("customer",)

    ordering = ("customer",)

    # Form view

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
            "TPE général",
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
            "Paramétrage des donations",
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
            "Paramétrage du contenu",
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
            "Paramétrage des redémarrages",
            {
                "fields": (
                    "restart",
                    "restart_every_day_from",
                    "restart_every_day_until",
                )
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # List view

    list_display = (
        "date",
        "amount",
        "amount_donated",
        "get_amount_donated_for_old_payments",
        "donation_formula",
        "status",
        "method",
    )

    list_filter = (
        "date",
        "donation_formula",
    )

    search_fields = ("payment_terminal",)

    ordering = ("-date",)

    # Form view

    fieldsets = (
        (
            None,
            {
                "fields": ("date",),
            },
        ),
        (
            None,
            {
                "fields": (
                    (
                        "terminal",
                        "payment_terminal",
                        "donation_formula",
                    ),
                    "donator",
                    (
                        "campaign",
                        "game",
                    ),
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    "amount",
                    "amount_donated",
                    "currency",
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    "method",
                    "status",
                )
            },
        ),
    )

    readonly_fields = ("date",)
