from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)
        
    return wrapper_func

# def allowed_users(allowd_roles=[]):
#     def decorator(view_func):
#         def wrapper_func(request, *args, **kwargs):
#             group=None
#             print('Working: ', allowd_roles,'User role: ',request.user.groups.all()[0].name )
#             if request.user.groups.exists():
#                 group = request.user.groups.all()[0].name

#             if group in allowd_roles:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return HttpResponse('You are not autorized to view this page')
            
#             return view_func(request, *args, **kwargs)
#         return wrapper_func
#     return decorator

def allowed_users(allowd_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group=None
            
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                print('Working: ', allowd_roles,'User role: ',request.user.groups.all()[0].name )
            if group in allowd_roles:
                return view_func(request, *args, **kwargs)
            else:
                #return HttpResponse('You are not autorized to view this page')
                return HttpResponseRedirect(reverse('account_login'))
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator