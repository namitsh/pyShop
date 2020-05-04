from django.contrib.auth import login, authenticate

import datetime
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, BookInstance, Author, Profile
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, login_required
from django.db import transaction
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.mixins import PermissionRequiredMixin

from .forms import RenewBookForm, UserForm, ProfileForm, IssueBookForm, SignUpForm

from random import randint

import uuid

from django.views.generic import (
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
    ListView
)

from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

def index(request, *args, **kwargs):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.all().count()

    # session count, how many times vistor has access the home page
    random_index = randint(5, num_books - 1)
    books_list = Book.objects.all()[:random_index]

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
        'book_list': books_list
    }

    return render(request, 'index.html', context)


class BookListView(ListView):
    model = Book
    # context_object_name = 'my_book_list'  # your own name for the list as a template variable
    template_name = 'books/book-list.html'
    paginate_by = 10

    # def get_queryset(self):
    # return Book.objects.filter(title__icontains='war')[:5]  # Get 5 books containing the title war


class BookCreateView(PermissionRequiredMixin, CreateView):
    model = Book
    template_name = 'books/books_edit.html'
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class BookUpdateView(PermissionRequiredMixin, UpdateView):
    model = Book
    template_name = 'books/books_edit.html'
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class BookDeleteView(PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/books_delete_confirm.html'
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('books')


class AuthorListView(ListView):
    model = Author
    # context_object_name = 'my_book_list'  # your own name for the list as a template variable
    template_name = 'authors/author-list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # # Call the base implementation first to get the context
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['page_title'] = 'Authors'
        return context

        # follow the pattern : 1. get existing context from superclass 2. add context information  3. return context


# class BookDetailView(DetailView):
#     template_name = 'books/book-detail.html'
#     model = Book

def BookDetailView(request, pk):
    obj = get_object_or_404(Book, pk=pk)
    head = obj.title
    print(head)
    avail_book = BookInstance.objects.filter(book__title__exact=head).filter(status__exact='a')[:1]
    context = {
        'object': obj,
        'available': 0
    }
    if avail_book:
        avail_book_id = uuid.uuid4()
        for item in avail_book:
            avail_book_id = item.id
        form = IssueBookForm(request.POST or None)
        book_ins = BookInstance.objects.get(id=avail_book_id)
        print(book_ins.status)
        print(request.user)
        if request.method == 'POST' and request.user:
            print(request.POST.get('Submit'))
            if form.is_valid():
                print('I am here')
                proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
                book_ins.due_date = proposed_renewal_date

                book_ins.borrower = request.user
                book_ins.status = 'o'
                book_ins.save()
                messages.success(request, _('Your profile is successfully updated'))

            else:
                form = IssueBookForm(None)

        context['avail_book'] = avail_book
        context['form'] = form
        context['available'] = 1

    return render(request, 'books/book-detail.html', context)


class AuthorDetailView(DetailView):
    template_name = 'authors/author-detail.html'
    model = Author


class AuthorCreateView(PermissionRequiredMixin, CreateView):
    model = Author
    template_name = 'authors/author_edit.html'
    fields = '__all__'
    initial = {'date_of_death': '05/01/2022'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdateView(UpdateView):
    model = Author
    template_name = 'authors/author_edit.html'
    fields = '__all__'
    # permission_required = 'catalog.can_mark_returned'


class AuthorDeleteView(PermissionRequiredMixin, DeleteView):
    model = Author
    template_name = 'authors/author_delete_confirm.html'
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class LoanedByUserListView(LoginRequiredMixin, ListView):
    model = BookInstance
    template_name = 'book_instance/bookinstance_list_borrowed_user.html'

    # paginate_by = 1

    def queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_date')


class LoanedByAllListView(PermissionRequiredMixin, ListView):
    """Generic class-based view listing all books on loan. Only visible to user with can mark_returned permissions"""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    # Or multiple permissions
    template_name = 'book_instance/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_date')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_date = form.cleaned_data['renewal_date']
            book_instance.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance
    }

    return render(request, 'book_instance/book_renewal_librarian.html', context)


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST or None, instance=request.user)
        profile_form = ProfileForm(request.POST or None, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            profile_form.save()
            messages.success(request, _('Your profile is successfully updated'))
            return redirect('index')
        else:
            messages.error(request, _('Please correct the error below'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profiles/edit_profile.html', context)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/profile.html'


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.location = form.cleaned_data.get('location')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required()
def read_pdf(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if book_instance.pdf:
        print('Yes')

    context = {
        'object': book_instance
    }

    return render(request, 'book_instance/pdf-reader.html', context)

