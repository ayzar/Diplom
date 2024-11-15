from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import TimeSlotGenerationForm
from .models import Service, Master, Client, Booking, Review, Portfolio, ServiceCategory, TimeSlot
from .utils import generate_time_slots_for_master


admin.site.register(Client)
admin.site.register(Booking)
admin.site.register(Review)

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['master', 'description']


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration', 'price')
    list_filter = ('category',)


class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(ServiceCategory, ServiceCategoryAdmin)  # Регистрация с использованием администраторского класса
admin.site.register(Service, ServiceAdmin)


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'experience', 'rating')
    filter_horizontal = ('categories', 'services')  # Добавляем поле 'services' для отображения услуг
    actions = ['generate_slots']

    def generate_slots(self, request, queryset):
        # Если запрос отправлен
        if 'apply' in request.POST:
            form = TimeSlotGenerationForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                master = queryset.first()  # Генерация слотов для выбранного мастера
                generate_time_slots_for_master(master, start_date, end_date)
                self.message_user(request,
                                  f"Слоты успешно сгенерированы для мастера {master.name} с {start_date} по {end_date}.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = TimeSlotGenerationForm()

        # Отображаем форму
        return render(request, 'admin/generate_slots_form.html', {'form': form, 'masters': queryset})


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('master', 'start_time', 'end_time', 'is_available')
