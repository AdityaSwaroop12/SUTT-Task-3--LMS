from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Sum
import os
from django.http import HttpResponse
from django.conf import settings
import pandas as pd
from django.contrib import messages
from Home.models import Book
from .models import UploadedFile
from django.db.models import Q
from .forms import UserProfileForm
from .models import UserProfile
from .models import UserProfile1
from .forms import UserProfile1Form
from django.shortcuts import get_object_or_404

#username - aditya
#password - sutt#*back

def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('profile_list')
    else:
        form = UserProfileForm()
    return render(request, 'create_profile.html', {'form': form})

def create_profile1(request):
    if request.method == 'POST':
        form = UserProfile1Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('profile_list1')
    else:
        form = UserProfile1Form()
    return render(request, 'create_profile1.html', {'form': form})

def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if there are available copies to borrow
    if book.total_copies > 0:
        # Decrease total copies and increase borrowed count
        book.total_copies -= 1
        book.borrowed_count += 1
        book.save()

        return redirect('borrowed_books')  # Redirect to borrowed books page
    else:
        # Handle case where no copies are available to borrow
        return render(request, 'error_page.html', {'error': 'No copies left to borrow.'})
def borrowed_books(request):
    # Get all books that have been borrowed at least once
    books = Book.objects.filter(borrowed_count__gte=1)

    # Calculate the total number of books borrowed
    total_borrowed_count = sum(book.borrowed_count for book in books)

    # Pass the books and total borrowed count to the template
    return render(request, 'borrow_books.html', {
        'books': books,
        'borrowed_count': total_borrowed_count,
    })

def profile_list(request):
    profiles = UserProfile.objects.all()
    return render(request, 'profile_list.html', {'profiles': profiles})

def profile_list1(request):
    profiles1 = UserProfile1.objects.all()
    return render(request, 'profile_list1.html', {'profiles': profiles1})

def index(request):
    return render(request, 'index.html')

def profile(request):
    return render(request, 'profile.html')

def form(request):
    if request.method == "POST":
        title = request.POST.get('title')
        author = request.POST.get('author')
        publisher = request.POST.get('publisher')
        isbn = request.POST.get('isbn')
        total_copies = request.POST.get('total_copies')
        image = request.FILES.get('image')

        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, "A book with this ISBN already exists.")
            return render(request, 'form.html')

        # Save book information in the database
        new_book = Book(title=title, author=author, publisher=publisher,
                        isbn=isbn, total_copies=total_copies, image=image)
        new_book.save()

        return redirect('/books')  # Redirect to the list or search page

    return render(request, 'form.html')

def index1(request):
    if request.user.is_anonymous:
        return redirect("/login")
    borrowed_count = Book.objects.aggregate(total_borrowed=Sum('borrowed_count'))['total_borrowed'] or 0
    return render(request, 'index1.html', {'borrowed_count': borrowed_count})

def index2(request):
    if request.user.is_anonymous:
        return redirect("/login1")
    return render(request, 'index2.html')

def about(request):
    return render(request, 'about.html')

def loginUser(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = User.objects.get(email = email.lower()).username
        user = authenticate(username = username , password = password)
        if user is not None:
            login(request,user)
            return redirect("/index1")
        else:
            return redirect("/login")
    return render(request, 'login.html')

def loginUser1(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username , password = password)
        if user is not None:
            login(request,user)
            return redirect("/index2")
        else:
            return redirect("/login1")
    return render(request, 'login1.html')

def download_template(request):
    # Define the template file path
    file_path = os.path.join(settings.BASE_DIR, 'templates', 'book_template.xlsx')

    # Serve the file for download
    with open(file_path, 'rb') as template:
        response = HttpResponse(template.read(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=book_template.xlsx'
        return response

def upload_books(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        # Save file to the database
        uploaded_file = UploadedFile.objects.create(file=excel_file)

        try:
            # Process the file using pandas
            df = pd.read_excel(uploaded_file.file.path)

            for _, row in df.iterrows():
                Book.objects.create(
                    title=row['Title'],
                    author=row['Author'],
                    publisher=row['Publisher'],
                    isbn=row['ISBN'],
                    total_copies=row['Total_Copies'],
                )
            messages.success(request, 'Books successfully uploaded!')

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")

    return render(request, 'upload_books.html')

def display_books(request):
    query = request.GET.get('query', '')
    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
    return render(request, 'display_books.html', {'books': books})

def logoutUser(request):
    logout(request)
    return redirect("/login")

def logoutUser1(request):
    logout(request)
    return redirect("/login1")
