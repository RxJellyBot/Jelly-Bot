from collections import OrderedDict
from dataclasses import dataclass
from typing import List

from JellyBotAPI.SystemConfig import Database

from django.utils.translation import gettext_lazy as _


@dataclass
class TermExplanation:
    term: str
    description: str
    example: str


@dataclass
class TermsCollection:
    name: str
    terms: List[TermExplanation]


terms_collection = OrderedDict()

terms_collection["Core"] = TermsCollection(
    _("Core"),
    [TermExplanation(_("Operation"),
                     _("The system has two ways to control: on the website, using the API. "
                       "Some actions may only available at a single side."),
                     _(""))
     ]
)
terms_collection["Features"] = TermsCollection(
    _("Features"),
    [TermExplanation(_("Auto-Reply"),
                     _("When the system receives/sees a word, it will reply back certain word(s) if it is set."),
                     _("User A setup an Auto-Reply module, which keyword is **A** and reply is **B**. Then, "
                       "he typed **A** wherever Jelly BOT can see, so Jelly BOT will reply **B** back.")),
     TermExplanation(_("Token Action"),
                     _(f"Because the lack of some key information, the system will enqueue your actions for "
                       f"{Database.TokenActionExpirySeconds // 3600:d} hrs. The user must use the issued token on "
                       f"the other side of the application to complete the action."),
                     _("User B created an Auto-Reply module on the website and choose the issue token option. "
                       "Then, he used that token with the setup command, then the module was registered.")),
     ]
)
