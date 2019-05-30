from django.utils.translation import gettext as _
from django.views import View

from JellyBotAPI import keys
from JellyBotAPI.views.render import render_template, simple_str_response
from extutils.gidentity import get_identity_data, IDIssuerIncorrect
from mongodb.factory import MixedUserManager, InsertOutcome


class RegisterAPIUserView(View):
    PASS_SIGNAL = "PASS"

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return render_template(request, "login.html", {"title": _("Login")})

    # noinspection PyMethodMayBeStatic, PyUnusedLocal, PyBroadException
    def post(self, request, *args, **kwargs):
        s = _("An unknown error occurred.")
        s_contact = " " + _("Contact the administrator of the website.")
        token = None

        try:
            result = MixedUserManager.register_google(get_identity_data(request.POST.get("idtoken")))
            if InsertOutcome.data_found(result.outcome):
                s = RegisterAPIUserView.PASS_SIGNAL
                token = result.idt_reg_result.token
            elif result.outcome == InsertOutcome.FAILED_NOT_EXECUTED:
                s = _("Registration process not performed.")
            elif result.outcome == InsertOutcome.FAILED_NOT_ACKNOWLEDGED:
                s = _("New user data creation failed.")
            elif result.outcome == InsertOutcome.FAILED_NOT_SERIALIZABLE:
                s = _("Wrong data has passed into the server.")
            else:
                s = _("An unknown error occurred during the new user data registration.")
        except IDIssuerIncorrect as ex1:
            s = str(ex1)
        except Exception as ex2:
            # NOTE: Insert `raise ex2` when any error occurred during login
            # raise ex2
            s += f" {ex2}"

        if s != RegisterAPIUserView.PASS_SIGNAL:
            s += s_contact

        response = simple_str_response(request, s)

        if token is not None:
            response.set_cookie(keys.USER_TOKEN, token)

        if s == RegisterAPIUserView.PASS_SIGNAL and token is None:
            return simple_str_response(request, _(f"User token is null while login succeed.{s_contact}"))
        else:
            return response
