from django.contrib import admin

from .models import Book, Genre, Language, BookInstance, Author, Profile


# Register your models here.

# define admin calss
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', "date_of_death")
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_date', 'id', 'borrower')
    list_filter = ('status', 'due_date')
    fieldsets = (
        (None, {
            'fields' : ('book', 'imprint', 'id', 'pdf')
        }),
        ('Availability',{
            'fields' :('status', 'due_date', 'borrower')
        })
    )

# register the admin class with associated model
admin.site.register(Author, AuthorAdmin)


# admin.site.register(Book)
admin.site.register(Language)
admin.site.register(Genre)
admin.site.register(Profile)
# admin.site.register(BookInstance)
# admin.site.register(Author)
