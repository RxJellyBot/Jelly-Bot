from markdown2 import Markdown


class CustomMarkdown(Markdown):
    def preprocess(self, text):
        return text


markdown = CustomMarkdown(extras=["fenced-code-blocks"])
