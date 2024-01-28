from django.contrib import admin

from terminal.models import Payment


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
