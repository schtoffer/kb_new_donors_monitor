import geopandas as gpd
import json
import os

# Create a more accurate representation of Norwegian counties
# This is a simplified version but much more accurate than rectangles

counties = {
    "Oslo": {
        "coordinates": [
            [[10.6, 59.8], [10.9, 59.8], [10.9, 60.0], [10.8, 60.1], [10.7, 60.05], [10.65, 59.95], [10.6, 59.8]]
        ]
    },
    "Akershus": {
        "coordinates": [
            [[10.4, 59.6], [11.2, 59.6], [11.3, 59.8], [11.2, 60.1], [11.0, 60.2], [10.7, 60.15], [10.5, 60.0], [10.4, 59.8], [10.4, 59.6]]
        ]
    },
    "Vestland": {
        "coordinates": [
            [[4.5, 60.0], [7.0, 60.0], [7.2, 60.5], [7.0, 61.0], [6.5, 61.5], [5.8, 61.8], [5.0, 61.5], [4.7, 61.0], [4.5, 60.5], [4.5, 60.0]]
        ]
    },
    "Rogaland": {
        "coordinates": [
            [[5.0, 58.0], [6.5, 58.0], [6.8, 58.5], [6.5, 59.0], [5.8, 59.3], [5.3, 59.2], [5.0, 58.8], [5.0, 58.0]]
        ]
    },
    "Trøndelag": {
        "coordinates": [
            [[10.0, 62.5], [13.5, 62.5], [14.0, 63.0], [13.8, 63.5], [13.5, 64.0], [13.0, 64.5], [12.0, 64.8], [11.0, 64.5], [10.5, 64.0], [10.0, 63.5], [10.0, 62.5]]
        ]
    },
    "Buskerud": {
        "coordinates": [
            [[9.0, 59.5], [10.5, 59.5], [10.6, 60.0], [10.4, 60.3], [9.8, 60.5], [9.5, 60.3], [9.2, 60.0], [9.0, 59.8], [9.0, 59.5]]
        ]
    },
    "Østfold": {
        "coordinates": [
            [[10.8, 59.0], [11.6, 59.0], [11.7, 59.3], [11.6, 59.5], [11.4, 59.7], [11.0, 59.7], [10.8, 59.5], [10.8, 59.0]]
        ]
    },
    "Agder": {
        "coordinates": [
            [[7.0, 57.8], [8.5, 57.8], [9.0, 58.0], [9.0, 58.5], [8.8, 58.8], [8.5, 59.0], [8.0, 59.2], [7.5, 59.0], [7.0, 58.5], [7.0, 57.8]]
        ]
    },
    "Vestfold": {
        "coordinates": [
            [[9.5, 59.0], [10.5, 59.0], [10.6, 59.3], [10.4, 59.5], [10.0, 59.5], [9.8, 59.3], [9.5, 59.0]]
        ]
    },
    "Innlandet": {
        "coordinates": [
            [[9.0, 60.5], [12.0, 60.5], [12.2, 61.0], [12.0, 61.5], [11.5, 62.0], [11.0, 62.3], [10.5, 62.0], [10.0, 61.5], [9.5, 61.0], [9.0, 60.8], [9.0, 60.5]]
        ]
    },
    "Nordland": {
        "coordinates": [
            [[11.0, 65.0], [17.0, 65.0], [17.5, 66.0], [17.0, 67.0], [16.0, 68.0], [14.0, 68.5], [13.0, 68.0], [12.0, 67.0], [11.5, 66.0], [11.0, 65.0]]
        ]
    },
    "Troms og Finnmark": {
        "coordinates": [
            [[18.0, 68.0], [28.0, 68.0], [30.0, 69.0], [29.0, 70.0], [27.0, 71.0], [24.0, 71.5], [21.0, 71.0], [19.0, 70.0], [18.0, 69.0], [18.0, 68.0]]
        ]
    },
    "Møre og Romsdal": {
        "coordinates": [
            [[5.0, 62.0], [8.0, 62.0], [8.2, 62.3], [8.0, 62.6], [7.5, 62.8], [7.0, 62.7], [6.0, 62.5], [5.5, 62.3], [5.0, 62.0]]
        ]
    },
    "Viken": {
        "coordinates": [
            [[9.5, 59.0], [12.0, 59.0], [12.2, 59.5], [12.0, 60.0], [11.5, 60.5], [11.0, 60.8], [10.5, 60.5], [10.0, 60.0], [9.8, 59.5], [9.5, 59.0]]
        ]
    }
}

# Create GeoJSON structure
features = []
for county, data in counties.items():
    feature = {
        "type": "Feature",
        "properties": {"name": county},
        "geometry": {
            "type": "Polygon",
            "coordinates": data["coordinates"]
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Write to file
with open('static/data/norway_counties_accurate.geojson', 'w') as f:
    json.dump(geojson, f)

print("Created more accurate Norway counties GeoJSON file.")
