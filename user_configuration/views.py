from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from user_configuration.forms import UserLoginForm


def staff_login(request):
    """
    staff login view. this view authenticates users using either their email or username. users that have already been
    authenticated are automatically redirected to their dashboard.
    :param request: django request object
    :return: HTML page to redirect to
    """
    if request.user.is_authenticated:
        return redirect('user_configuration:dashboard')
    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            user = authenticate(username=form_data['email_or_pass'], password=form_data['password'])
            if user is not None:
                # set the timezone based on the middleware described in user_configuration/middleware.py
                request.session['django_timezone'] = 'Africa/Lagos'
                login(request, user)
                # todo: consider using memcached for all this
                # todo: TOMORROW: LEARN ABOUT SASS MIXINS
                return redirect('user_configuration:dashboard')
            else:
                messages.error(request, "Invalid Credentials!")
                return redirect("user_configuration:staff-login")
    else:
        form = UserLoginForm()
        context = {
            'login_form': form
        }
        return render(request, "login.html", context)


@login_required()
def dashboard(request):
    user = request.user
    context = {"user": user}
    return render(request, "dashboard.html", context)
