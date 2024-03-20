from django.db import models


class Location(models.Model):
    address = models.CharField('адрес', max_length=200, unique=True)
    lat = models.DecimalField('широта', max_digits=9, decimal_places=6)
    lon = models.DecimalField('долгота', max_digits=9, decimal_places=6)
    query_date = models.DateTimeField('дата запроса')

    def __str__(self):
        return f'{self.address} {self.lat} {self.lon}'