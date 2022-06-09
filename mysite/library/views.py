from django.shortcuts import render, get_object_or_404, redirect, reverse
from . models import Book, Author, BookInstance
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from . forms import BookReviewForm
from django.views.generic.edit import FormMixin


def index(request):
    
    # # Suskaičiuokime keletą pagrindinių objektų
    # num_books = Book.objects.all().count()
    # num_instances = BookInstance.objects.all().count()
    
    # # Laisvos knygos (tos, kurios turi statusą 'g')
    # num_instances_available = BookInstance.objects.filter(status__exact='g').count()
    
    # # Kiek yra autorių    
    # num_authors = Author.objects.count()

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='g').count()
    num_authors = Author.objects.count()
    
    # Papildome kintamuoju num_visits, įkeliame jį į kontekstą.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    
    # perduodame informaciją į šabloną žodyno pavidale:
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # renderiname index.html, su duomenimis kintamąjame context
    response = render(request, 'index.html', context=context)
    return response


def authors(request):
    paginator = Paginator(Author.objects.all(), 2)
    page_number = request.GET.get('page')
    paged_authors = paginator.get_page(page_number)
    # authors = Author.objects.all()
    context = {
        'authors': paged_authors
    }
    return render(request, 'authors.html', context=context)


def author(request, author_id):
    single_author = get_object_or_404(Author, pk=author_id)
    return render(request, 'author.html', {'author': single_author})


def search(request):
    """
    paprasta paieška. query ima informaciją iš paieškos laukelio,
    search_results prafiltruoja pagal įvestą tekstą knygų pavadinimus ir aprašymus.
    Icontains nuo contains skiriasi tuo, kad icontains ignoruoja ar raidės 
    didžiosios/mažosios.
    """
    query = request.GET.get('query')
    query_filter = Q(title__icontains=query) | Q(summary__icontains=query)
    search_results = Book.objects.filter(query_filter)
    return render(request, 'search.html', {'books': search_results, 'query': query})


@csrf_protect
def register(request):
    if request.method == "POST":
        # duomenu surinkimas
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        # validuosim forma, tikrindami ar sutampa slaptažodžiai, ar egzistuoja vartotojas
        error = False
        if not password or password != password2:
            messages.error(request, _('Slaptažodžiai nesutampa arba neįvesti.'))
            error = True
        if not username or User.objects.filter(username=username).exists():
            messages.error(request, _('Vartotojas {} jau egzistuoja arba neįvestas.').format(username))
            error = True
        if not email or User.objects.filter(email=email).exists():
            messages.error(request, _('Vartotojas su el.praštu {} jau egzistuoja arba neįvestas.').format(email))
            error = True
        if error:
            return redirect('register')
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, _('Vartotojas {} užregistruotas sėkmingai. Galite prisijungti').format(username))
            return redirect('index')
    return render(request, 'register.html')


class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    template_name = 'book_list.html'    
    # patys galite nustatyti šablonui kintamojo vardą
    context_object_name = 'book_list'
    # gauti sąrašą 3 knygų su žodžiu pavadinime 'ir'
    # queryset = Book.objects.filter(title__icontains='ir')[:3] 
    # šitą jau panaudojome. Neįsivaizduojate, kokį default kelią sukuria :)
    # template_name = 'books/my_arbitrary_template_name_list.html' 

    def get_queryset(self):
        return Book.objects.all()[:3] 


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    context_object_name = 'books'
    template_name ='user_books.html'
    paginate_by = 10
    
    def get_queryset(self):
        # BookInstance.objects.taken_books_read_by_me_ordered_by_due_back()
        # BookInstance.objects.taken().order_by_due_back().read_by_me()
        # BookInstance.objects.filter(reader=self.request.user).filter(status__exact='p').order_by('due_back')
        return BookInstance.objects.filter(reader=self.request.user).taken().order_by_due_back()


class BookByUserDetailView(LoginRequiredMixin, generic.DetailView):
    model = BookInstance
    template_name = 'user_book.html'


class BookDetailView(FormMixin, generic.DetailView):
    model = Book
    template_name = 'book_detail.html'
    form_class = BookReviewForm

    class Meta:
        ordering = ['title']

    # nurodome, kur atsidursime komentaro sėkmės atveju.
    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.id})

    # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # štai čia nurodome, kad knyga bus būtent ta, po kuria komentuojame, o vartotojas bus tas, kuris yra prisijungęs.
    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super(BookDetailView, self).form_valid(form)
