from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
import uuid


class Genre(models.Model):
    name = models.CharField(_('name'), max_length=200, help_text=_('Name of the genre (for example: detective, sci-fi, horror...)'))
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')


class Book(models.Model):
    """Modelis reprezentuoja knygą (bet ne specifinę knygos kopiją)"""
    title = models.CharField(_('title'), max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True, related_name='books', verbose_name=_('author'))
    summary = models.TextField(_('description'), max_length=1000, help_text=_('Short book description'))
    isbn = models.CharField('ISBN', max_length=13, help_text=_('13 symbols: <a href="https://www.isbn-international.org/content/what-isbn">ISBN code</a>'))
    genre = models.ManyToManyField(Genre, help_text=_('choose genre(s) for this book'), verbose_name=_('genre'))
    cover = models.ImageField(_('cover'), upload_to='covers', null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Nurodo konkretaus aprašymo galinį adresą"""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    display_genre.short_description = _('genre')


class BookInstanceQuerySet(models.QuerySet):
    def read_by_me(self, user):
        return self.filter(reader=user)
    
    def taken(self):
        return self.filter(status__exact="p")

    def reserved_or_taken(self):
        return self.filter(models.Q(status__exact="p") | models.Q(status__exact="r"))

    def order_by_due_back(self):
        return self.order_by("due_back")

    def taken_books_read_by_me_ordered_by_due_back(self, user):
        return self.taken().read_by_me(user).order_by_due_back()


class BookInstance(models.Model):
    """Modelis, aprašantis konkrečios knygos kopijos būseną"""
    objects = BookInstanceQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_('Unique ID for each book instance'))
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True, verbose_name=_('book')) 
    due_back = models.DateField(_('due back'), null=True, blank=True)
    reader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('user'))

    LOAN_STATUS = (
        ('a', _('Managed')),
        ('p', _('Taken')),
        ('g', _('Available')),
        ('r', _('Reserved')),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='a',
        verbose_name=_('status'),
    )

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        ordering = ['due_back']

    def __str__(self):
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    description = HTMLField(_('description'))

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name} {self.first_name}'

    def display_books(self):
        return ', '.join(book.title for book in self.books.all()[:3])
    display_books.short_description = _('books')


class BookReview(models.Model):
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('book'))
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('reviewer'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('date created'))
    content = models.TextField(_('review'), max_length=2000)
