# Create your views here.

from users.forms import  ChooseIdentityForm, EditProfileForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, REDIRECT_FIELD_NAME
from django.template.context import Context, RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from misc.dajaxice.core import dajaxice_functions
from users.models import ERPUser
from misc.utilities import get_position

def redirectToLogin(request):
    return HttpResponseRedirect('/login/')

def login(request):

    #Redirect logged in users
    if request.user.is_authenticated():
        return HttpResponseRedirect('/dash/')

    if request.method == 'POST':

        #Authenticate the user
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)

        #if everything is in order
        if user is not None and user.is_active and not user.is_superuser:
            auth_login(request, user)

            #Set things about the user. I am assuming that status, subdept etc are set a priori for users without multiple identities.

            #check for multiple identities
            if user.erpuser.multiple_ids == True:  
                return HttpResponseRedirect('/choose_identity/')
    
            return HttpResponseRedirect('/dash/')
    
        #If the username and password aren't in order
        invalid_login = True
        return render_to_response('users/login.html', locals(), context_instance=RequestContext(request))
    
    #rendering for the initial GET request
    else:
        return render_to_response('users/login.html', locals(), context_instance=RequestContext(request))

def logout(request):
    """
        View for logging out users from the session.
    """
    if request.user.is_authenticated():
        auth_logout(request)
    return HttpResponseRedirect('/login/')


@login_required
def choose_identity ( request ):
    
    #This is a Boolean which informs the template that the user has made no error
    noerror = True

    if request.method == 'POST':
        identity_form = ChooseIdentityForm (request.user.erpuser, request.POST)
        if identity_form.is_valid():
            cd = identity_form.cleaned_data
            userprofile = request.user.erpuser

            #if he's chosen only a coordship
            if (not cd['coordships'] == None) and (cd['supercoordships'] == None) and (cd['coreships'] == None):
                userprofile.status = 0
                currentsubdept = cd['coordships']
                userprofile.subdept = currentsubdept
                userprofile.dept = currentsubdept.dept
                userprofile.save()
                return HttpResponseRedirect ('/dash/')
            
            #if he's chosen a supercoordship
            elif (cd['coordships'] == None) and (not cd['supercoordships'] == None) and (cd['coreships'] == None):
                userprofile.status = 1 #supercoord
                userprofile.dept = cd['supercoordships']
                userprofile.subdept = None
                userprofile.save()
                return HttpResponseRedirect ('/dash/')
                
            elif (cd['coordships'] == None) and (cd['supercoordships'] == None) and (not cd['coreships'] == None):
                userprofile.status = 2 #core
                userprofile.dept = cd['coreships']
                userprofile.subdept = None
                userprofile.save()
                return HttpResponseRedirect ('/dash/')
                
            else:
                noerror = False
                return render_to_response ( 'dash/choose_identity.html', locals(), context_instance = RequestContext(request) )
            
            
    identity_form = ChooseIdentityForm ( curruser = request.user.erpuser )
    return render_to_response ( 'dash/choose_identity.html', locals(), context_instance = RequestContext(request) )
