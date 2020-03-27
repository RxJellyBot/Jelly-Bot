from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.utils.translation import gettext_lazy as _

from JellyBot import keys
from JellyBot.components.mixin import LoginRequiredMixin
from JellyBot.utils import get_root_oid, get_post_keys
from JellyBot.views import render_template, simple_str_response, simple_json_response
from extutils.locales import locales, languages
from extutils.dt import now_utc_aware, localtime
from extutils.gidentity import get_identity_data, IDIssuerIncorrect
from extutils.emailutils import MailSender
from mongodb.factory import RootUserManager
from mongodb.factory.results import WriteOutcome


class AccountLoginView(View):
    PASS_SIGNAL = "PASS"

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def get(self, request, *args, **kwargs):
        return render_template(request, _("Login"), "account/login.html")

    # noinspection PyMethodMayBeStatic, PyUnusedLocal, PyBroadException
    def post(self, request, *args, **kwargs):
        s = str(_("An unknown error occurred."))
        s_contact = " " + str(_("Contact the administrator of the website."))
        token = None

        try:
            result = RootUserManager.register_google(get_identity_data(request.POST.get("idtoken")))
            if result.outcome.is_success:
                s = AccountLoginView.PASS_SIGNAL
                token = result.idt_reg_result.token
            elif result.outcome == WriteOutcome.X_NOT_EXECUTED:
                s = _("Registration process not performed.")
            elif result.outcome == WriteOutcome.X_NOT_ACKNOWLEDGED:
                s = _("New user data creation failed.")
            elif result.outcome == WriteOutcome.X_NOT_SERIALIZABLE:
                s = _("The data cannot be passed into the server.")
            else:
                s = _(
                    "An unknown error occurred during the new user data registration. "
                    "Code: {} / Registration Code: {}.").format(
                    result.outcome.code, result.idt_reg_result.outcome.code)

            if not result.outcome.is_success:
                MailSender.send_email_async(
                    f"Result: {result.serialize()}<br>"
                    f"Outcome: {result.outcome}<br>"
                    f"Exception: {result.exception}<br>"
                    f"Registration: {result.idt_reg_result.outcome}<br>"
                    f"Registration Exception: {result.idt_reg_result.exception}<br>",
                    subject="New user data registration failed"
                )
        except IDIssuerIncorrect as ex1:
            s = str(ex1)
        except Exception as ex2:
            # EXNOTE: Insert `raise ex2` when any error occurred during login
            raise ex2
            s += f" ({ex2})"

        if s != AccountLoginView.PASS_SIGNAL:
            s += s_contact

        response = simple_json_response(s)

        if token is not None:
            response.set_cookie(keys.Cookies.USER_TOKEN, token)

        if s == AccountLoginView.PASS_SIGNAL and token is None:
            return simple_json_response(_("User token is null however login succeed. {}").format(s_contact))
        else:
            return response


class AccountLogoutView(View):
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        response = render_template(request, _("Logout"), "account/logout.html")
        response.delete_cookie(keys.Cookies.USER_TOKEN)
        try:
            del request.session[keys.Session.USER_ROOT_ID]
            request.session.modified = True
        except KeyError:
            pass

        return response


class AccountSettingsPageView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        config = RootUserManager.get_config_root_oid(get_root_oid(request))

        return render_template(
            self.request, _("Account Settings"), "account/settings.html",
            {"locale_list": sorted(locales, key=lambda item: item.description),
             "lang_list": sorted(languages, key=lambda item: item.code),
             "current_config": config})

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        update_result = RootUserManager.update_config(get_root_oid(request), **get_post_keys(request.POST))

        if update_result.success:
            return simple_str_response(
                request,
                f"success/{localtime(now_utc_aware()):%m-%d %H:%M:%S (%Z)} - "
                f"{_('Account settings updated.')}")
        else:
            return simple_str_response(
                request,
                f"danger/{localtime(now_utc_aware()):%m-%d %H:%M:%S (%Z)} - "
                f"{_('Account settings failed to update.')}")
