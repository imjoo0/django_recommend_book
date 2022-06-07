# user/views.py
from django.shortcuts import render, redirect
from .models import UserModel
from book.models import Book
from django.http import HttpResponse
# user/views.py
from django.contrib.auth import get_user_model  # 사용자가 있는지 검사하는 함수
# user/views.py
from django.contrib import auth  # 사용자 auth 기능
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup

def sign_up_view(request):
    bestseller = crawling_bestseller()
    if request.method == 'GET':
        user = request.user.is_authenticated  # 로그인 된 사용자가 요청하는지 검사
        if user:  # 로그인이 되어있다면
            return redirect('/')
        else:  # 로그인이 되어있지 않다면
            return render(request, 'signup.html', {'bestseller':bestseller})
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        my_book = request.POST.get('book', '')
        my_title=bestseller[int(my_book)-1]['title']
        my_img=bestseller[int(my_book)-1]['img']
        print(my_title)
        if password != password2:
            # 패스워드가 다르다는 에러가 필요합니다. {'error':'에러문구'} 를 만들어서 전달합니다.
            return render(request, 'signup.html', {'error': '패스워드를 확인 해 주세요!'})
        else:
            if username == '' or password == '':
                # 사용자 저장을 위한 username과 password가 필수라는 것을 얘기 해 줍니다.
                return render(request, 'signup.html', {'error': '사용자 이름과 패스워드는 필수 값 입니다'})

            exist_user = get_user_model().objects.filter(username=username)
            if exist_user:
                return render(request, 'signup.html',
                              {'error': '사용자가 존재합니다.'})  # 사용자가 존재하기 때문에 사용자를 저장하지 않고 회원가입 페이지를 다시 띄움
            else:
                UserModel.objects.create_user(username=username, password=password)
                first_book=Book()
                first_book.title = my_title
                first_book.img_url = my_img
                first_book.pub_date = 12
                first_book.description = 'description'
                first_book.save()

                return redirect('/sign-in')  # 회원가입이 완료되었으므로 로그인 페이지로 이동


# user/views.py

def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', "")
        password = request.POST.get('password', "")

        me = auth.authenticate(request, username=username, password=password)  # 사용자 불러오기
        if me is not None:  # 저장된 사용자의 패스워드와 입력받은 패스워드 비교
            auth.login(request, me)
            return redirect('/')
        else:
            crawling_bestseller()
            return render(request,'signin.html',{'error':'유저이름 혹은 패스워드를 확인 해 주세요'})  # 로그인 실패
    elif request.method == 'GET':
        user = request.user.is_authenticated
        if user:
            return redirect('/')
        else:
            return render(request, 'signin.html')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def user_follow(request, id):
    me = request.user
    click_user = UserModel.objects.get(id=id)
    if me in click_user.followee.all():
        click_user.followee.remove(request.user)
    else:
        click_user.followee.add(request.user)
    return redirect('/')


def profile_view(request):
    if request.method == 'GET':
        return render(request, 'profile.html')


def crawling_bestseller():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('http://www.kyobobook.co.kr/bestSellerNew/bestseller.laf', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')
    books = soup.select('#main_contents > ul > li')
    bestseller=[]
    c=0
    for book in books:
        c +=1
        best_image = book.select_one('div.cover > a > img')
        bestseller.append({'rank':c ,'title':best_image['alt'], 'img':best_image['src']})
    return bestseller