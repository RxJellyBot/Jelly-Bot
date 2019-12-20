import random
from collections import defaultdict

from django.utils.translation import gettext_lazy as _

from extutils import safe_cast
from flags import BotFeature
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from JellyBot.systemconfig import Bot

from ._base_ import CommandNode

cmd = CommandNode(
    codes=["rd", "rdm", "random"], order_idx=1500, name=_("Random"),
    description=_("Randomly generate a result."))


class OptionList:
    def __init__(self, txt: str):
        self.elements = list(set(txt.split(Bot.RandomChoiceSplitter)))
        self.weights = None
        self.elem_ignored = False

        if len(self.elements) > 1 and all([Bot.RandomChoiceWeightSplitter in elem for elem in self.elements]):
            temp = []
            self.weights = []

            for elem in self.elements:
                option, weight = elem.split(Bot.RandomChoiceWeightSplitter, 1)

                weight = safe_cast(weight, float)

                if weight:
                    self.weights.append(weight)
                    temp.append(option)
                else:
                    self.elem_ignored = True

            self.elements = temp

    def __len__(self):
        return len(self.elements)

    @property
    def has_weights(self) -> bool:
        return self.weights is not None

    def pick_one(self):
        return random.choices(self.elements, self.weights, k=1)[0]

    def pick_multi(self, count: int) -> dict:
        results = random.choices(self.elements, self.weights, k=count)

        counter = defaultdict(lambda: 0)

        for result in results:
            counter[result] += 1

        return counter


elem_help_txt = _(
    "Options to be picked. Use two continuous spaces/blanks (`{}`) to separate options.\n\n"
    "- The count of the options cannot exceed {}.\n\n"
    "- If **ALL** options exists single space/blank (`{}`), then this "
    "will be considered as a **weighted** option list. The options picked will base on their weight.\n\n"
    "- Weights can be either float, integer, or both.\n\n"
    "- Duplicated option will be automatically ignored.\n\n"
    "\n\n"
    "Example:\n\n"
    "- Option List **without** weights: A{}B{}C\n\n"
    "- Option List **with** weights: A{}0.7{}B{}0.5{}C{}0.9").format(
    Bot.RandomChoiceSplitter, Bot.RandomChoiceOptionLimit, Bot.RandomChoiceWeightSplitter,
    Bot.RandomChoiceSplitter, Bot.RandomChoiceSplitter,
    Bot.RandomChoiceSplitter, Bot.RandomChoiceWeightSplitter, Bot.RandomChoiceSplitter,
    Bot.RandomChoiceWeightSplitter, Bot.RandomChoiceSplitter
)
option_overlimit_txt = _("Maximum count of options is {}.").format(Bot.RandomChoiceOptionLimit)
pick_overlimit_txt = _(
    "Maximum count of picking an option in a single command is {}.").format(Bot.RandomChoiceCountLimit)


# noinspection PyUnusedLocal
@cmd.command_function(
    feature_flag=BotFeature.TXT_RDM_CHOICE_ONE,
    arg_count=1,
    arg_help=[elem_help_txt]
)
def random_once(e: TextMessageEventObject, elements: str):
    option_list = OptionList(elements)

    if len(option_list) > Bot.RandomChoiceOptionLimit:
        return [
            HandledMessageEventText(
                content=option_overlimit_txt)]

    ctnt = [_("Option Picked: {}").format(option_list.pick_one())]

    if option_list.elem_ignored:
        ctnt.append("")
        ctnt.append(_("*There are element(s) ignored possibly because the options are misformatted.*"))

    return [HandledMessageEventText(content="\n".join([str(c) for c in ctnt]))]


# noinspection PyUnusedLocal
@cmd.command_function(
    feature_flag=BotFeature.TXT_RDM_CHOICE_MULTI,
    arg_count=2,
    arg_help=[elem_help_txt,
              _("Count of how many times to randomly pick an option.\n"
                "This number cannot exceed {}.").format(Bot.RandomChoiceCountLimit)]
)
def random_multi(e: TextMessageEventObject, elements: str, times: int):
    ret = []

    if times > Bot.RandomChoiceCountLimit:
        return [HandledMessageEventText(content=pick_overlimit_txt)]

    option_list = OptionList(elements)

    if len(option_list) > Bot.RandomChoiceOptionLimit:
        return [HandledMessageEventText(content=option_overlimit_txt)]

    results = sorted(option_list.pick_multi(times).items(), key=lambda kv: kv[1], reverse=True)

    if option_list.elem_ignored:
        ret.append(_("There are element(s) ignored possibly because the options are misformatted."))

    ret.append("\n".join([f"{option}: {count} ({count / times:.2%})" for option, count in results]))

    return [HandledMessageEventText(content=ctnt) for ctnt in ret]
