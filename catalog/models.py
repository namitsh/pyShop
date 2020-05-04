from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    favorite_Genre = models.ManyToManyField('Genre', help_text='Select your favourite genre', blank=True)
    wish_list = models.ManyToManyField('Book', help_text='Select your to-read books')
    profile_picture = models.ImageField(upload_to='profile_pictures/', default=None, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Genre(models.Model):
    name = models.CharField(max_length=60, help_text="Enter a book Genre (e.g. Science Fiction)")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200, help_text='Enter book title')
    summary = models.TextField(max_length=1000, help_text="enter the brief description of book")
    isbn = models.CharField('ISBN', max_length=13)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    genre = models.ManyToManyField('Genre', help_text="Select a genre for a book")
    image = models.ImageField(upload_to='images/')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={"pk": self.id})

    # defining display genre because genre is many to many, we cant display all at once, it would be costly.
    # it returns a string. it isd used in admin. py in list display as 'display_genre
    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    # it is overriding the name of display_ genre on admin site
    display_genre.short_description = 'Genre'


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def get_absolute_url(self):
        return reverse('author-detail', kwargs={"pk": self.id})

    def __str__(self):
        return f'{self.first_name}, {self.last_name}'


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular book in library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pdf = models.FileField(upload_to='documents/', null=True)

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
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return f'{self.id}, {self.book.title}'

    @property
    def is_overdue(self):
        if self.due_date and self.due_date < date.today():
            return True
        return False


class Language(models.Model):
    name = models.CharField(max_length=100, help_text='Enter language of the book(e.g. English, French)')

    def __str__(self):
        return self.name
