import sys
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from salon.models import Master
from salon.utils import generate_time_slots_for_master

# Добавление директории проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class Command(BaseCommand):
    help = 'Generates time slots for a master within a given date range.'

    def add_arguments(self, parser):
        # Вместо type=str и использования nargs
        parser.add_argument('master_id', type=int, help="ID of the master for whom to generate slots")
        parser.add_argument('start_date', type=str, help="Start date in format YYYY-MM-DD HH:MM")
        parser.add_argument('end_date', type=str, help="End date in format YYYY-MM-DD HH:MM")

    def handle(self, *args, **options):
        master_id = options['master_id']

        # Преобразуем строки в datetime
        start_date = datetime.strptime(options['start_date'], '%Y-%m-%d %H:%M')
        end_date = datetime.strptime(options['end_date'], '%Y-%m-%d %H:%M')

        try:
            master = Master.objects.get(id=master_id)
        except Master.DoesNotExist:
            self.stdout.write(self.style.ERROR('Master not found!'))
            return

        self.stdout.write(
            self.style.SUCCESS(f'Generating time slots for {master.name} from {start_date} to {end_date}.'))

        # Вызовем функцию для генерации слотов
        generate_time_slots_for_master(master, start_date, end_date)

        self.stdout.write(self.style.SUCCESS(f'Successfully generated time slots for {master.name}.'))
