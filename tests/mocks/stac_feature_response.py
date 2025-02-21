from .feature_model import feature_with_bands


class MockStacFeatureResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    @staticmethod
    def iter_content(chunk_size):
        yield b"dummydata"

    @staticmethod
    def json():
        return feature_with_bands
