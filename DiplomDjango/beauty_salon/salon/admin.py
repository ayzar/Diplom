from django.contrib import admin
from .models import Category, Service, Master, Client, Booking, Review, Portfolio

admin.site.register(Category)
admin.site.register(Service)
admin.site.register(Master)
admin.site.register(Client)
admin.site.register(Booking)
admin.site.register(Review)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['master', 'description']