from datetime import timedelta
from typing import List

from django.template import loader

from extutils.utils import str_reduce_length
from flags import ExtraContentType
from JellyBot.systemconfig import Database
from models.field import (
    ExtraContentTypeField, TextField, DateTimeField, GeneralField, ObjectIDField
)

from ._base import Model
from .field import ModelDefaultValueExt


class ExtraContentModel(Model):
    Type = ExtraContentTypeField("tp")
    Title = TextField("t", default=ModelDefaultValueExt.Optional)
    Content = GeneralField("c", default=ModelDefaultValueExt.Required)
    Timestamp = DateTimeField("e", default=ModelDefaultValueExt.Required)
    ChannelOid = ObjectIDField("ch", default=ModelDefaultValueExt.Optional)

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
        elif model.type == ExtraContentType.AUTO_REPLY_SEARCH:
            return ExtraContentHTMLTransformer._trans_ar_search_(model)
        else:
            return f"Unhandled extra content type: {model.type}"

    @staticmethod
    def _trans_ex_message_(model: ExtraContentModel) -> str:
        if not model.content:
            return ""

        tab_list: List[str] = []
        tab_content: List[str] = []

        for reason, content in model.content:
            common_key = f"msg-{id(content)}"

            tab_list.append(
                f'<a class="list-group-item list-group-item-action" '
                f'id="list-{common_key}" '
                f'data-toggle="list" href="#{common_key}" role="tab">'
                f'{str_reduce_length(content, 20, escape_html=True)}</a>')
            tab_content.append(
                f'<div class="tab-pane fade" id="{common_key}" role="tabpanel" '
                f'aria-labelledby="list-{common_key}"><h4>{reason}</h4>{content}</div>')

        return f'<div class="row">' \
               f'<div class="col-4"><div class="list-group" id="list-tab" role="tablist">{"".join(tab_list)}' \
               f'</div></div>' \
               f'<div class="col-8"><div class="tab-content" id="nav-tabContent">{"".join(tab_content)}</div>' \
               f'</div></div>'

    @staticmethod
    def _trans_ar_search_(model: ExtraContentModel) -> str:
        from mongodb.factory import ChannelManager, AutoReplyManager
        from mongodb.helper import IdentitySearcher

        if not model.content:
            return ""

        tab_list: List[str] = []
        tab_content: List[str] = []

        module_list = list(AutoReplyManager.get_conn_list_oids(model.content))

        uids = []
        for module in module_list:
            uids.append(module.creator_oid)
            if not module.active and module.remover_oid:
                uids.append(module.remover_oid)

        username_dict = {}
        if model.channel_oid:
            username_dict = IdentitySearcher.get_batch_user_name(
                uids, ChannelManager.get_channel_oid(model.channel_oid))

        for module in module_list:
            common_key = f"msg-{id(module)}"
            content = loader.render_to_string("ar/module-card.html",
                                              {"username_dict": username_dict, "module": module})

            tab_list.append(
                f'<a class="list-group-item list-group-item-action" '
                f'id="list-{common_key}" '
                f'data-toggle="list" href="#{common_key}" role="tab">{module.keyword.content_html}</a>')
            tab_content.append(
                f'<div class="tab-pane fade" id="{common_key}" role="tabpanel" '
                f'aria-labelledby="list-{common_key}">{content}</div>')

        return f'<div class="row">' \
               f'<div class="col-4"><div class="list-group" id="list-tab" role="tablist">{"".join(tab_list)}' \
               f'</div></div>' \
               f'<div class="col-8"><div class="tab-content" id="nav-tabContent">{"".join(tab_content)}</div>' \
               f'</div></div>'
