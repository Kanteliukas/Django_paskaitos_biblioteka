from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, BookReview

class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ("book", "status", 'reader', 'due_back', 'id')
    list_filter = ("status", "due_back")
    list_editable = ('due_back', 'status')
    fieldsets = (
        ("General", {"fields": ("id", "book")}),
        ("Availability", {"fields": ('status', 'due_back', 'reader')}),
    )

    search_fields = ("id", "book__title")


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    readonly_fields = ("id",)
    can_delete = False
    extra = 0  # išjungia placeholder'ius


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "display_genre")
    inlines = [BooksInstanceInline]

class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "display_books")

class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'date_created', 'reviewer', 'content')


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(BookReview, BookReviewAdmin)
