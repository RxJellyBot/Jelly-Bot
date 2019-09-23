from collections import OrderedDict
from dataclasses import dataclass
from typing import List

from JellyBot.sysconfig import Database

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
                     _("-"))
     ]
)
terms_collection["Features"] = TermsCollection(
    _("Features"),
    [TermExplanation(_("Auto-Reply"),
                     _("When the system receives/sees a word, it will reply back certain word(s) if it is set."),
                     _("User A setup an Auto-Reply module, which keyword is **A** and reply is **B**. Then, "
                       "somebody typed **A** wherever Jelly BOT can see, so Jelly BOT will reply **B** back.")),
     TermExplanation(_("Token Action"),
                     _("The users provide partial required information for an operation, then the system will yield a "
                       "token to the users for completing it while holding it for {:d} hrs.<br>"
                       "Users will need to use the given token with the lacking information for completing the "
                       "operation before it expires.").format(Database.TokenActionExpirySeconds // 3600),
                     _("User B created an Auto-Reply module on the website and choose the issue token option. "
                       "Then, he submit the token in the channel, so the Auto-Reply module is registered.")),
     TermExplanation(_("Profile System/Permission"),
                     _("Users can have multiple profiles in the channel for various features use. Profiles will have "
                       "some permission or their privilege attached.<br>Some profiles may be granted by votes from "
                       "channel members or assigned by channel manager.<br>"
                       "This system is similar to the role system of **Discord**."),
                     _("ChannelA have profiles called **A** with admin privilege and **B** for normal users.<br>"
                       "Users who have profile **A** assigned will be able to use features that only admins can use.")),
     TermExplanation(_("Channel Management"),
                     _("Users will be able to adjust the settings specifically designated to the channel. "
                       "The availability of what can be adjusted will base on the user's profile."),
                     _("Eligibility of accessing the pinned auto-reply module, "
                       "changing the admin/mod of a channel...etc.")),
     ]
)
