from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Publisher(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class AuthorDetail(models.Model):
    sex = models.BooleanField(max_length=1, choices=((0, '男'), (1, '女'),))
    email = models.EmailField()
    address = models.CharField(max_length=50)
    birthday = models.DateField()
    author = models.OneToOneField(Author)


class Myuser(models.Model):
    sex = models.BooleanField(max_length=1, choices=((0, '男'), (1, '女'),))
    email = models.EmailField()
    address = models.CharField(max_length=50)
    birthday = models.DateField()
    telephone = models.CharField(max_length=11)
    user = models.OneToOneField(User)


class Classify(models.Model):
    name = models.CharField(max_length=32, default='文学')


class Book(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
    classify = models.ForeignKey(Classify, default=1)
    publisher = models.ForeignKey(Publisher)
    publication_date = models.DateField()
    price = models.DecimalField(max_digits=5, decimal_places=2, default=10)

    def __str__(self):
        return self.title
