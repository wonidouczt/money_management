from django.shortcuts import render
from django.http import HttpResponse

from django.views import View
import datetime

# Create your views here.


# def index(request):
#
#     books = BookInfo.objects.all()
#     context = {'books': books}
#
#     # render函数，第一个参数request；第二个参数模板文件;第三个参数context传参
#     # context = {'name': '如花'}
#     return render(request, 'index.html', context)
#     return HttpResponse('hahahaha')

# ###########################类视图######################################
class LoginView(View):

    def get(self, request):
        username = request.GET.get('username')
        context = {
            'username': username,
            'age': 14,
            'birthday': datetime.datetime.now(),
            'money': {
                '2019': 12000,
                '2020': 20000,
            }
        }
        return render(request, 'index.html', context)




    def post(self, request):
        return HttpResponse('validate login')
