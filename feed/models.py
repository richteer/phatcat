from django.db import models
from django.contrib.auth.models import User

# Uses django built in User because laze


# The Cat to be fed
class Cat(models.Model):

	name = models.CharField(max_length=64)
	owner = models.ForeignKey(User) # TODO: figure out on_delete

	def __str__(self):
		return self.name

# Table for when the cat was fed and by whom
class Fed(models.Model):

	FOOD_CHOICES = (
		('0', 'undefined'),
		('1', 'Dry'),
		('2', 'Wet'),
	)

	time = models.DateTimeField()
	food = models.CharField(max_length=1, choices=FOOD_CHOICES)
	by = models.ForeignKey(User)
	cat = models.ForeignKey(Cat)

# Relation between user and 
class Feeder(models.Model):

	user = models.ForeignKey(User)
	cat = models.ForeignKey(Cat) # TODO: figure out on_delete
