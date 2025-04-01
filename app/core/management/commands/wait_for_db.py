import time
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as psycopg2opError
from django.db.utils import OperationalError




class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Waiting For Database")
        db_up = False
        i = 1
        while db_up is False and i <=5:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError, psycopg2opError) :
                self.stdout.write("Trying Again")
                i+=1
                time.sleep(1)
        if db_up is False:
            self.stdout.write("Enable to connect")
        else:
            self.stdout.write(self.style.SUCCESS("DATABASE AVAILABLE"))

