import pytz
from datetime import timedelta, time
from django.utils import timezone
from .models import TimeSlot

# Получаем московский часовой пояс
moscow_tz = pytz.timezone('Europe/Moscow')


def generate_time_slots_for_master(master, start_date, end_date):
    # Проверяем, что мастер передан и даты корректны
    if not master:
        print("Ошибка: мастер не найден!")
        return

    if start_date >= end_date:
        print("Ошибка: Начальная дата не может быть больше или равна конечной.")
        return

    # Убедимся, что start_date и end_date имеют часовой пояс (являются aware датами)
    if start_date.tzinfo is None:
        start_date = moscow_tz.localize(start_date)  # Преобразуем в московское время
    if end_date.tzinfo is None:
        end_date = moscow_tz.localize(end_date)  # Преобразуем в московское время

    # Определяем, сколько времени будет длиться каждый слот (например, 30 минут)
    slot_duration = timedelta(minutes=60)

    current_time = start_date
    time_slots = []  # Список для слотов, которые будем сохранять

    # Конкретное время начала и окончания рабочего дня
    work_start_time = time(10, 0)  # 10:00
    work_end_time = time(20, 0)  # 20:00

    # Создаем временные слоты, пока текущее время не достигнет конечной даты
    while current_time < end_date:
        # Преобразуем текущее время в московское
        current_time_moscow = current_time.astimezone(moscow_tz)

        # Проверяем, что текущее время попадает в рабочие часы (с 10:00 до 20:00)
        if current_time_moscow.time() >= work_start_time and current_time_moscow.time() < work_end_time:
            end_time = current_time + slot_duration

            # Проверяем, что слот не пересекается с существующими
            existing_slot = TimeSlot.objects.filter(master=master, start_time=current_time).exists()
            if not existing_slot:
                # Создаём новый слот
                slot = TimeSlot(
                    master=master,
                    start_time=current_time,
                    end_time=end_time,
                    is_available=True
                )
                time_slots.append(slot)

        # Перемещаемся на следующий слот
        current_time += slot_duration

    # Сохраняем все слоты
    if time_slots:
        TimeSlot.objects.bulk_create(time_slots)
        print(f"Создано {len(time_slots)} слотов для мастера {master.name} с {start_date} по {end_date}.")
    else:
        print("Нет слотов для генерации.")
