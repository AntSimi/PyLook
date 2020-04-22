import logging
import matplotlib.figure as mfigure

logger = logging.getLogger("pylook")


class Figure(mfigure.Figure):
    def set_suptitle(self, title):
        self.suptitle(title)

    def get_suptitle(self):
        text = self._suptitle
        return text if text is None else text.get_text()

    def axes_properties_message(self, axes_id, properties):
        logger.trace(f"Receive properties from {axes_id}")
        for id_, child in self.child_id.items():
            if id_ == axes_id:
                continue
            child.set_axes_with_message(properties)
