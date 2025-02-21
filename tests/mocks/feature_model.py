feature_without_bands = {
    "type": "Feature",
    "id": "ABC123",
    "collection": "y",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [-48.3106, -15.3637],
                [-48.3106, -16.4178],
                [-47.2492, -16.4178],
                [-47.2492, -15.3637],
                [-48.3106, -15.3637],
            ]
        ],
    },
    "bbox": [-48.3106, -16.4178, -47.2492, -15.3637],
    "properties": {
        "datetime": "X",
        "path": 1,
        "row": 1,
        "satellite": "W",
        "sensor": "S",
        "cloud_cover": 0,
    },
    "assets": {
        "thumbnail": {"type": "X", "href": "http://a.b/t.png"},
    },
}

feature_with_bands = {
    "type": "Feature",
    "id": "ABC123",
    "collection": "y",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [-48.3106, -15.3637],
                [-48.3106, -16.4178],
                [-47.2492, -16.4178],
                [-47.2492, -15.3637],
                [-48.3106, -15.3637],
            ]
        ],
    },
    "bbox": [-48.3106, -16.4178, -47.2492, -15.3637],
    "properties": {
        "datetime": "X",
        "path": 1,
        "row": 1,
        "satellite": "W",
        "sensor": "S",
        "cloud_cover": 0,
    },
    "assets": {
        "thumbnail": {"type": "X", "href": "http://a.b/t.png"},
        "blue": {"type": "X", "href": "http://test.dev/image.tif"},
    },
}
