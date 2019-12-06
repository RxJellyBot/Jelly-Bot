import random
from collections import defaultdict

from django.utils.translation import gettext_lazy as _

from flags import BotFeature
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from JellyBot.systemconfig import Bot

from ._base_ import CommandNode

cmd = CommandNode(
    codes=["rd", "rdm", "random"], order_idx=1500, name=_("Random"),
    description=_("Randomly generate a result."))


class OptionList:
    def __init__(self, txt: str):
        self.elements = list(set(txt.split(Bot.RandomChoiceSplittor)))
        self.weights = None

        if len(self.elements) > 1 and all([Bot.RandomChoiceWeightSplittor in elem for elem in self.elements]):
            temp = []
            self.weights = []

            for elem in self.elements:
                option, weight = elem.split(Bot.RandomChoiceWeightSplittor, 2)

                self.weights.append(float(weight))
                temp.append(option)

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
    Bot.RandomChoiceSplittor, Bot.RandomChoiceOptionLimit, Bot.RandomChoiceWeightSplittor,
    Bot.RandomChoiceSplittor, Bot.RandomChoiceSplittor,
    Bot.RandomChoiceSplittor, Bot.RandomChoiceWeightSplittor, Bot.RandomChoiceSplittor,
    Bot.RandomChoiceWeightSplittor, Bot.RandomChoiceSplittor
)
option_overlimit_txt = _("Maximum count of options is {}.").format(Bot.RandomChoiceOptionLimit)
pick_overlimit_txt = _(
    "Maximum count of picking an option in a single command is {}.").format(Bot.RandomChoiceCountLimit)


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

    return [
        HandledMessageEventText(
            content=_("Option Picked: {}").format(option_list.pick_one())
        )
    ]


@cmd.command_function(
    feature_flag=BotFeature.TXT_RDM_CHOICE_MULTI,
    arg_count=2,
    arg_help=[elem_help_txt,
              _("Count of how many times to randomly pick an option.\n"
                "This number cannot exceed {}.").format(Bot.RandomChoiceCountLimit)]
)
def random_multi(e: TextMessageEventObject, elements: str, times: int):
    if times > Bot.RandomChoiceCountLimit:
        return [HandledMessageEventText(content=pick_overlimit_txt)]

    option_list = OptionList(elements)

    if len(option_list) > Bot.RandomChoiceOptionLimit:
        return [HandledMessageEventText(content=option_overlimit_txt)]

    results = sorted(option_list.pick_multi(times).items(), key=lambda kv: kv[1], reverse=True)

    return [
        HandledMessageEventText(
            content="\n".join(
                [f"{option}: {count} ({count / times:.2%})" for option, count in results])
        )
    ]
