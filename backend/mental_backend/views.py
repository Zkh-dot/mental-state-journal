from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpRequest, JsonResponse
from .models import journal, users, users_salt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
import bcrypt
from django.contrib.auth import authenticate, login

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
            id = int(request.POST.get('id'))
            password = request.POST.get('password')
            salt = bcrypt.gensalt()
            try:
                name = request.POST.get("name")
            except:
                name = ''

            if users.add_user(
                    user_id=id, 
                    user_name=name, 
                    user_password=bcrypt.hashpw(bytes(password, "utf-8"), salt)
                ):
                users_salt.add_salt(id, salt)
                return HttpResponse("user added!")
            else:
                return HttpResponse("user existed!")
        except Exception as e:
            return HttpResponseBadRequest(str(e) + '\n' + str(e.__traceback__.tb_frame) + '\n' + str(e.__traceback__.tb_lineno))
     
@csrf_protect
@csrf_exempt    
def login_user(request: HttpRequest):
    if request.method == "POST":
        id = int(request.POST.get('id'))
        password = request.POST.get('password')
        salt = users_salt.get_salt(id)
        user = users.auth_user(user_id=id, password=bcrypt.hashpw(bytes(password, "utf-8"), salt))
        if user is not None:
            login(request, user)
            return HttpResponse('You are authenticated')
        
    return HttpResponse('something got wrong, check your id and password')

    
def create_post(request: HttpRequest):
    if request.user.is_authenticated:
        pass    

def echo(request: HttpRequest):
    return HttpResponse('hi') 