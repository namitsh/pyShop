from django.urls import path
from . import views
from django.conf.urls import url, include

urlpatterns = [
    path('', views.index, name='index'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('books/', views.BookListView.as_view(), name='books'),
    # path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('book/<int:pk>', views.BookDetailView, name='book-detail'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('mybooks/', views.LoanedByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedByAllListView.as_view(), name='all-borrowed'),
    path('books/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('author/create/', views.AuthorCreateView.as_view(), name ='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdateView.as_view(), name = 'author-update'),
    path('author/<int:pk>/delete/', views.AuthorDeleteView.as_view(), name='author-delete'),
    path('book/create/',views.BookCreateView.as_view(), name='book-create'),
    path('book/<int:pk>/update/',views.BookUpdateView.as_view(), name='book-update'),
    path('book/<int:pk>/delete/',views.BookDeleteView.as_view(),name='book-delete'),
    path('edit_profile/', views.update_profile, name='edit-profile'),
    path('profile/<int:pk>', views.ProfileDetailView.as_view(), name='profile'),
    url(r'^signup/$', views.signup, name='signup'),
    path('read/<uuid:pk>', views.read_pdf, name='read-pdf')
]
