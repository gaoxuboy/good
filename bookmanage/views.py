from django.shortcuts import render, redirect, HttpResponse
from bookmanage.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.

def log_in(request):
    if request.path == '/user/':
        username = request.POST.get("user", '').strip()
        if not User.objects.filter(username=username):
            state = '用户不存在'
            return HttpResponse(json.dumps(state))
        elif User.objects.filter(username=username):
            return HttpResponse("ok")
    if request.path == "/login/":
        username = request.POST.get("user", '').strip()
        password = request.POST.get("pwd", '').strip()
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('/index/')
            # return redirect('%s' % request.path)

    return render(request, 'login.html')


def log_out(request):
    logout(request)
    return redirect('/login/')


def register(request):
    state = None
    if request.method == "POST":
        password = request.POST.get('pwd', '')
        repeat_password = request.POST.get('re_pwd', '')
        email = request.POST.get('email', '')
        if password == '' or repeat_password == '':
            state = 'empty'
        elif password != repeat_password:
            state = 'repeat_error'
        else:
            username = request.POST.get('re_user', '')
            if User.objects.filter(username=username):
                state = 'user_exist'
            else:
                new_user = User.objects.create_user(username=username, password=password, email=email)
                new_user.save()
                # new_my_user = Myuser(user=new_user, telephone=request.POST.get('telephone', ''))
                # new_my_user.save()

                return HttpResponse('ok')
    content = {
        'state': state,
        'user': None,
    }
    return HttpResponse(json.dumps(content))


@login_required
def index(request):
    book_list = Book.objects.all()

    user = request.user
    classify_list = Classify.objects.all()
    author_list = Author.objects.all()
    publish_list = Publisher.objects.all()
    paginator = Paginator(book_list, 5)
    page = request.GET.get('page', 1)
    currentPage = int(page)

    try:
        book_list = paginator.page(page)
    except PageNotAnInteger:
        book_list = paginator.page(1)
    except EmptyPage:
        book_list = paginator.page(paginator.num_pages)

    return render(request, 'index.html', locals())


@login_required
def search(request):
    se = request.POST.get("se", "")
    if not search:
        book_list = Book.objects.all()
    else:
        book_list = Book.objects.filter(Q(title__contains=se) | Q(authors__name__contains=se) |
                                        Q(price__contains=se) | Q(classify__name__contains=se) |
                                        Q(publisher__name__contains=se) | Q(publication_date__contains=se)).distinct()

    user = request.user
    classify_list = Classify.objects.all()
    author_list = Author.objects.all()
    publish_list = Publisher.objects.all()
    paginator = Paginator(book_list, 5)
    page = request.GET.get('page', 1)
    currentPage = int(page)

    try:
        book_list = paginator.page(page)
    except PageNotAnInteger:
        book_list = paginator.page(1)
    except EmptyPage:
        book_list = paginator.page(paginator.num_pages)

    return render(request, 'index.html', locals())


@login_required
def addbook(request):
    author_list = Author.objects.all()
    publish_list = Publisher.objects.all()
    classify_list = Classify.objects.all()
    print(request.method)

    if request.method == "POST":
        print(request.POST)
        title = request.POST.get('title')
        price = request.POST.get('price')
        date = request.POST.get('date')
        author = request.POST.getlist('author')
        publish = request.POST.get('publish')
        classify = request.POST.get('classify')
        book = Book.objects.create(title=title, price=price, publication_date=date, publisher_id=publish,
                                   classify_id=classify)
        book.authors.add(*Author.objects.filter(id__in=author))
        return redirect('/index/')
    return render(request, 'addbook.html', locals())


def edit(request):
    if request.method == "POST":
        book_id = request.POST.get('id')
        title = request.POST.get('title')
        price = request.POST.get('price')
        date = request.POST.get('date')
        author = request.POST.getlist('author[]')
        classify = request.POST.get('classify')
        publish = request.POST.get('publish')
        Book.objects.filter(id=book_id).update(title=title, price=price, publication_date=date, publisher_id=publish,
                                               classify_id=classify)
        book = Book.objects.filter(id=book_id).first()
        book.authors.remove(*Author.objects.all())
        book.authors.add(*author)
        print(title, price, date, author, publish)
        print(type(title), type(price), type(date), type(author), type(publish))

        book_dict = {}
        book_dict['title'] = title
        book_dict['price'] = str(book.price)
        book_dict['date'] = str(book.publication_date)
        book_dict['author'] = [i["authors__name"] for i in Book.objects.filter(id=book_id).values("authors__name")]
        book_dict['classify'] = Book.objects.filter(id=book_id).values("classify__name").first()["classify__name"]
        book_dict['publish'] = Book.objects.filter(id=book_id).values("publisher__name").first()["publisher__name"]

        print(json.dumps(book_dict))

        return HttpResponse(json.dumps(book_dict))


def dell(request):
    if request.method == "POST":
        print(request.POST)
        book_id = request.POST.get('id', 0)

        Book.objects.get(id=book_id).delete()

        return HttpResponse(json.dumps('ok'))


@login_required
def mima(request):
    user = request.user
    state = None
    if request.path == '/mima/':
        old_pwd = request.POST.get('old_pwd', '')
        if old_pwd == '':
            state = '请输入密码'
        elif not user.check_password(old_pwd):
            state = '密码错误'
        content = {
            'user': str(user),
            'state': state
        }

        return HttpResponse(json.dumps(content))
    new_password = request.POST.get('new_pwd')
    user.set_password(new_password)
    user.save()
    return HttpResponse(json.dumps("修改成功"))
