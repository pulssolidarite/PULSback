from django.contrib import admin

from .models import Terminal, Donator, Session, Payment

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
    )

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
            "Paramétrage général",
            {
                "fields": (
                    "play_timer",
                    "free_mode_text",
                    "payment_terminal",
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
    )

    readonly_fields = ("date",)


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
