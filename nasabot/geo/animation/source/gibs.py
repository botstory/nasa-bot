class GIBSSource:
    def __init__(self, pattern, **kwargs):
        self.pattern = pattern
        self.values = kwargs

    def get_url_by_frame(self, frame):
        return self.pattern.format(**{**self.values, **frame})
