import matplotlib.figure as mfigure


class Figure(mfigure.Figure):
    def set_suptitle(self, title):
        self.suptitle(title)

    def get_suptitle(self):
        text = self._suptitle
        return text if text is None else text.get_text()
