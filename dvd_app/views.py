from django.shortcuts import render, redirect
from django.views.generic.edit import FormView, View
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages

from django.views.generic.base import ContextMixin, TemplateResponseMixin


from django.views.generic.edit import UpdateView

from .models import Copil, Binevoitor
from .forms import LoginForm, SignupForm, MainFilterForm, UpdateUserForm, EmailForm, UpdateParolaForm
from .mixins import UserLoggedIn

import datetime
import uuid
import hashlib

# Create your views here.
class LoginView(FormView):
    template_name = "dvd_app/login_view.html"
    form_class = LoginForm
    success_url = reverse_lazy("dvd_app:main_view")

    def form_valid(self, form):
        try:
            bv = Binevoitor.objects.get(
                email=form.cleaned_data['email'],
                parola=str(hashlib.sha256(form.cleaned_data['parola'].encode('utf-8')).hexdigest())
            )
        except Binevoitor.DoesNotExist:
            messages.error(self.request, "Date de logare invalide!")
            return self.form_invalid(form)

        self.request.session['logged_in_user'] = bv.id
        messages.success(self.request, "Login cu succes!")
        return super(LoginView, self).form_valid(form)

class EmailParolaView(FormView):
    template_name = "dvd_app/mail_pt_parola.html"
    form_class = EmailForm
    success_url = reverse_lazy("dvd_app:login")

    def form_valid(self, form):
        try:
            bv = Binevoitor.objects.get(
                email=form.cleaned_data['email']
            )
        except Binevoitor.DoesNotExist:
            messages.error(self.request, "Acest email nu apartine nici unui utilizator")
            return self.form_invalid(form)

        bv.password_change_key = uuid.uuid4().hex
        bv.save(update_fields=["password_change_key"])
        reset_url = self.request.build_absolute_uri(reverse('dvd_app:parola_noua', args=[bv.password_change_key]))

        bv.send_password_reset(reset_url)
        messages.info(self.request,"Ti-am trimis un mail cu pasii pe care trebuie sa-i urmezi.\nVerifica si in spam!")
        return super(EmailParolaView, self).form_valid(form)

class UpdateParolaView(FormView):
    template_name = "dvd_app/actualizare_parola.html"
    form_class = UpdateParolaForm
    success_url = reverse_lazy("dvd_app:login")

    def dispatch(self, request, *args, **kwargs):
        try:
            self.binevoitor = Binevoitor.objects.get(password_change_key=kwargs['password_change_key'])
        except Exception as e:
            return redirect("dvd_app:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bv"] = self.binevoitor
        return context

    def form_valid(self, form):
        parola_noua = form.cleaned_data["parola_noua"]
        confirma_parola = form.cleaned_data["confirma_parola"]

        if parola_noua != confirma_parola:
            messages.error(self.request, "Parolele nu corespund!")
            return self.form_invalid(form)

        self.binevoitor.parola = str(hashlib.sha256(parola_noua.encode('utf-8')).hexdigest())
        self.binevoitor.password_change_key = None
        self.binevoitor.save(update_fields=['parola', 'password_change_key'])
        messages.success(self.request, "Parola v-a fost schimbata cu succes!")
        return super(UpdateParolaView, self).form_valid(form)

class SignupView(FormView):
    template_name = "dvd_app/signup_view.html"
    form_class = SignupForm
    success_url = reverse_lazy("dvd_app:main_view")

    def form_valid(self, form):
        if Binevoitor.objects.filter(email=form.cleaned_data['email']).exists():
            messages.error(self.request, "Exista deja un utilizator cu acest email")
            return self.form_invalid(form)
        new_binevoitor = Binevoitor(
            email=form.cleaned_data['email'],
            parola=str(hashlib.sha256(form.cleaned_data['parola'].encode('utf-8')).hexdigest()),
            nume=form.cleaned_data['nume'],
            telefon=form.cleaned_data['telefon'],
        )
        new_binevoitor.save()
        self.request.session['logged_in_user'] = new_binevoitor.id

        messages.success(self.request, "Contul a fost creat cu succes!")
        return super(SignupView, self).form_valid(form)


class UpdateUserView(UserLoggedIn, UpdateView):
    model = Binevoitor
    form_class = UpdateUserForm
    template_name = 'dvd_app/actualizeaza_date.html'
    success_url = reverse_lazy('dvd_app:main_view')

    def get_object(self, queryset=None):
        binevoitor_id = self.request.session.get('logged_in_user')
        return Binevoitor.objects.get(id=binevoitor_id)

    def form_valid(self, form):
        messages.success(self.request, "Datele dumneavoastra au fost modificate cu succes!")
        return super().form_valid(form)


class MainView(UserLoggedIn, FormView):
    template_name = "dvd_app/main_view.html"
    form_class = MainFilterForm
    success_url = reverse_lazy

    def get_form_kwargs(self):
        return {"varste_ramase": Copil.get_varste_ramase()}

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context["all_good"] = Copil.objects.filter(binevoitor=None).count() == 0
        return context

    def post(self, request):
        form = MainFilterForm(
            request.POST,
            varste_ramase=Copil.get_varste_ramase(),
        )
        if not form.is_valid():
            if form.cleaned_data["varsta"] and not form.cleaned_data["gen"]:
                return self.render_to_response({'form': form})

        _filter = {
            'binevoitor': None
        }

        if not form.cleaned_data["varsta"] == "-1":
            _filter['varsta'] = form.cleaned_data["varsta"]

        if not form.cleaned_data["gen"] == "NONE":
            _filter['gen'] = form.cleaned_data["gen"]

        copil = Copil.objects.filter(**_filter).order_by('?').first()
        if not copil:
            messages.error(
                self.request,
                "Din fericire toti copii cu aceasta varsta si gen si-au gasit un binevoitor!"
            )
            return self.form_invalid(form)
        return redirect("dvd_app:confirm_copil", copil.id)


class ConfirmCopilView(UserLoggedIn, FormView):
    template_name = "dvd_app/confirm_view.html"
    success_url = reverse_lazy("dvd_app:main_view")

    def get(self, request, copil_id):
        try:
            copil = Copil.objects.get(id=copil_id)
        except Copil.DoesNotExist:
            messages.error(self.request, "Nu exista acest copil!")
            return redirect("dvd_app:main_view")
        return self.render_to_response({"copil": copil})

    def post(self, request, copil_id):
        try:
            copil = Copil.objects.get(id=copil_id)
        except Copil.DoesNotExist:
            messages.error(self.request, "Nu exista acest copil!")
            return redirect("dvd_app:main_view")

        if copil.binevoitor:
            messages.error(self.request, "Copilul nu mai este disponibil!")
            return redirect("dvd_app:main_view")

        copil.binevoitor_id = request.session["logged_in_user"]
        copil.save()

        messages.success(self.request, 'Felicitari, esti foarte darnic! Poti vedea detaliile copiilor carora le vei face cadou de la "Meniu"->"Copii mei".')
        return redirect("dvd_app:main_view")


class CopiiiMeiView(UserLoggedIn, View, TemplateResponseMixin, ContextMixin):
    template_name = "dvd_app/copiii_mei_view.html"

    def get(self, request):
        copii = Copil.objects.filter(binevoitor_id=self.request.session['logged_in_user'])
        return self.render_to_response({"copii": copii})


class CadouLivratView(UserLoggedIn, View):
    def get(self, request, copil_id):
        try:
            copil = Copil.objects.get(id=copil_id)
        except Copil.DoesNotExist:
            messages.error(request, "Copilul nu există!")
            return redirect("dvd_app:copiii_mei")

        if copil.binevoitor_id != request.session["logged_in_user"]:
            messages.error(request, "Nu ai permisiunea de a modifica datele acestui copil!")
            return redirect("dvd_app:copiii_mei")

        copil.daruit = not copil.daruit
        copil.save()

        if copil.daruit:
            messages.success(request, "Cadoul a fost marcat ca livrat!")
        else:
            messages.success(request, "Cadoul a fost marcat ca nelivrat!")

        return redirect("dvd_app:copiii_mei")


class ConfirmRenuntaView(UserLoggedIn, View, TemplateResponseMixin, ContextMixin):
    template_name = "dvd_app/confirm_renuntare.html"
    def get(self, request, copil_id):
        try:
            copil = Copil.objects.get(id=copil_id)
        except Copil.DoesNotExist:
            messages.error(request, "Copilul nu există!")
            return redirect("dvd_app:copiii_mei")

        if copil.binevoitor_id != request.session["logged_in_user"]:
            messages.error(request, "Nu ai permisiunea de a modifica datele acestui copil!")
            return redirect("dvd_app:copiii_mei")

        now = datetime.datetime.now()
        if now.month == 12 and now.day > 18:
            messages.error(request, "Nu poti renunta la un copil dupa 18 decembrie!")
            return redirect("dvd_app:copiii_mei")

        return render(request, "dvd_app/confirm_renuntare.html", {"copil": copil})

    def post(self, request, copil_id):
        try:
            copil = Copil.objects.get(id=copil_id)
        except Copil.DoesNotExist:
            messages.error(request, "Copilul nu există!")
            return redirect("dvd_app:copiii_mei")

        if copil.binevoitor_id != request.session["logged_in_user"]:
            messages.error(request, "Nu ai permisiunea de a modifica datele acestui copil!")
            return redirect("dvd_app:copiii_mei")

        now = datetime.datetime.now()
        if now.month == 12 and now.day > 18:
            messages.error(request, "Nu poti renunta la un copil dupa 18 decembrie!")
            return redirect("dvd_app:copiii_mei")

        # Dacă utilizatorul confirmă renunțarea, setam binevoitorul la nul
        copil.binevoitor = None
        copil.daruit = False
        copil.save()
        messages.success(request, "Ai renuntat la acest copil!😭")

        return redirect("dvd_app:copiii_mei")


class LogoutView(UserLoggedIn, View, TemplateResponseMixin, ContextMixin):
    template_name = "dvd_app/copiii_mei_view.html"

    def get(self, request):
        request.session.pop("logged_in_user")
        messages.success(request, "La revedere!")
        return redirect("dvd_app:login")

class DetaliiCopilView(UserLoggedIn, View, TemplateResponseMixin, ContextMixin):
    template_name = "dvd_app/detalii.html"

    def get(self, request, copil_id):
        try:
            copil = Copil.objects.get(id=copil_id)
        except Copil.DoesNotExist:
            messages.error(self.request, "Nu exista acest copil!")
            return redirect("dvd_app:main_view")

        if copil.binevoitor_id != request.session["logged_in_user"]:
            messages.error(request, "Nu ai permisiunea de a modifica datele acestui copil!")
            return redirect("dvd_app:copiii_mei")

        return self.render_to_response({"copil": copil})
