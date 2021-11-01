from contextlib import contextmanager


# copied from https://stackoverflow.com/a/7039175/5692176 (and wrapped in a class)
class TerminalLoadingAnimation:
    ANIMATION_CHARACTERS = ["|", "/", "-", "\\"]

    def __init__(self, loading_title=None):
        self._loading_title = loading_title or ""
        self._next_char_idx = 0

    def start(self):
        self.update()

    def update(self):
        print(self._next_line(), end="\r")

    def end(self):
        print(self._next_line(), end="\n")

    def _next_line(self):
        next_char = self.ANIMATION_CHARACTERS[
            self._next_char_idx % len(self.ANIMATION_CHARACTERS)
        ]
        self._next_char_idx += 1
        next_line = f"{next_char} {self._loading_title}"
        return next_line

    @staticmethod
    @contextmanager
    def open(loading_title):
        loading_animation = TerminalLoadingAnimation(loading_title)
        loading_animation.start()
        try:
            yield loading_animation
        finally:
            loading_animation.end()
