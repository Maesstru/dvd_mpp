
from django.shortcuts import redirect
from django.contrib import messages

class UserLoggedIn():
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("logged_in_user"):
            messages.error(self.request, "Autentifica-te intai!")
            return redirect('dvd_app:login')
        return super(UserLoggedIn, self).dispatch(request, *args, **kwargs)