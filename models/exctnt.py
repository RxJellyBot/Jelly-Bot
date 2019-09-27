from collections import Hashable
from datetime import timedelta
from typing import List

from extutils.utils import reduce_length
from flags import ExtraContentType
from JellyBot.systemconfig import Database
from models.field import (
    ExtraContentTypeField, TextField, DateTimeField,GeneralField
)

from ._base import Model, ModelDefaultValueExt


class ExtraContentModel(Model):
    Type = ExtraContentTypeField("tp")
    Title = TextField("t", default=ModelDefaultValueExt.Optional)
    Content = GeneralField("c", default=ModelDefaultValueExt.Required)
    Timestamp = DateTimeField("e", default=ModelDefaultValueExt.Required)
    
    @property
    def expires_on(self):
        return self.timestamp + timedelta(seconds=Database.ExtraContentExpirySeconds)

    @property
    def content_html(self) -> str:
        return ExtraContentHTMLTransformer.transform(self)


class ExtraContentHTMLTransformer:
    @staticmethod
    def transform(model: ExtraContentModel) -> str:
        if model.type == ExtraContentType.PURE_TEXT:
            return str(model.content)
        elif model.type == ExtraContentType.EXTRA_MESSAGE:
            return ExtraContentHTMLTransformer._trans_ex_message_(model)

    @staticmethod
    def _trans_ex_message_(model: ExtraContentModel) -> str:
        if model.content and len(model.content) > 0:
            tab_list: List[str] = []
            tab_content: List[str] = []

            for reason, content in model.content:
                common_key = f"msg-{id(content)}"

                tab_list.append(
                    f'<a class="list-group-item list-group-item-action" '
                    f'id="list-{common_key}" '
                    f'data-toggle="list" href="#{common_key}" role="tab">{reduce_length(content, 20)}</a>')
                tab_content.append(
                    f'<div class="tab-pane fade" id="{common_key}" role="tabpanel" '
                    f'aria-labelledby="list-{common_key}"><h4>{reason}</h4>{content}</div>')

            return f'<div class="row">' \
                   f'<div class="col-4"><div class="list-group" id="list-tab" role="tablist">{"".join(tab_list)}' \
                   f'</div></div>' \
                   f'<div class="col-8"><div class="tab-content" id="nav-tabContent">{"".join(tab_content)}</div>' \
                   f'</div></div>'
