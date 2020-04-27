from django.db import models
from django.urls import reverse
import uuid


# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=60, help_text="Enter a book Genre (e.g. Science Fiction)")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200, help_text='Enter book title')
    summary = models.TextField(max_length=1000, help_text="enter the brief description of book")
    isbn = models.CharField('ISBN', max_length=13)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    genre = models.ManyToManyField(Genre, help_text="Select a genre for a book")
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog:catalog-detail', kwargs={id: self.id})


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def get_absolute_url(self):
        return reverse('catalog:author-detail', kwargs={id: self.id})

    def __str__(self):
        return f'{self.first_name}, {self.last_name}'


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular book in library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)

    # a tuple containing tuples of key-value pairs

    LOAN_STATUS = (
        ('m', 'maintenance'),
        ('o', 'on loan'),
        ('r', 'reserved'),
        ('a', 'available')
    )
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book Availabilty')

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f'{self.id}, {self.book.title}'


class Language(models.Model):
    name = models.CharField(max_length=100, help_text='Enter language of the book(e.g. English, French)')

    def __str__(self):
        return self.name
