from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpRequest, JsonResponse
from .models import journal, users
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
import json


def check_if_user_valid(request: HttpRequest):
    if users.user_exists(user_id=request.headers.get('id')):
        return HttpResponse('yes')
    else: 
        return HttpResponse('no')

def get_user_name(request: HttpRequest):
    return HttpResponse(users.get_user_name(user_id=request.headers.get('id')))


def set_user_name(request: HttpRequest):
    if users.set_user_name(user_id=request.POST.get('id'), user_name=request.POST.get('name')):
        return HttpResponse('name is set to ' + users.get_user_name(request.POST.get('id')))
    else: 
        return HttpResponseBadRequest


@csrf_protect
@csrf_exempt 
def user_name_handler(request: HttpRequest):
    if request.method == "GET":
        return get_user_name(request)
    else:
        return set_user_name(request)

@csrf_protect
@csrf_exempt 
def add_user(request: HttpRequest):
    if request.method == 'POST':
        try:
            id = request.POST.get('id')
            try:
                name = request.POST.get("name")
            except:
                name = ''
            db_response = users.add_user(user_id=id, user_name=name)
            if db_response:
                return HttpResponse("user added!")
            else:
                return HttpResponse("user existed!")
        except Exception as e:
            return HttpResponseBadRequest()

    
def echo(request: HttpRequest):
    return HttpResponse('hi') 