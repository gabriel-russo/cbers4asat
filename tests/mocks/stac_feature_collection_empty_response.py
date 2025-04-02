class MockStacFeatureCollectionEmptyResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    @staticmethod
    def iter_content(chunk_size):
        yield b"dummydata"

    @staticmethod
    def json():
        return {
            "LGI-CDSR": {
                "Collection_A": {
                    "type": "FeatureCollection",
                    "features": [],
                },
            }
        }
