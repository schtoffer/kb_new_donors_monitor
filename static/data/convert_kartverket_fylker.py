import geopandas as gpd
import json
import os

def convert_kartverket_fylker():
    """
    Convert the Kartverket Fylker GeoJSON file to a format that Folium can understand.
    """
    print("Converting Kartverket Fylker GeoJSON file...")
    
    # Read the GeoJSON file with the original CRS
    input_file = 'static/data/Basisdata_0000_Norge_25833_Fylker_GeoJSON.geojson'
    print(f"Reading input file: {input_file}")
    
    # Specify the layer name explicitly
    gdf = gpd.read_file(input_file, layer='Fylke')
    
    print(f"CRS: {gdf.crs}")
    print(f"Number of features: {len(gdf)}")
    print(f"Columns: {gdf.columns.tolist()}")
    
    # Print a sample of the data
    print("\nSample data:")
    for col in ['fylkesnavn', 'fylkesnummer']:
        if col in gdf.columns:
            print(f"{col}: {gdf[col].head().tolist()}")
    
    # Convert to WGS84 (EPSG:4326) for web mapping
    print("\nConverting to WGS84 coordinate system...")
    gdf_wgs84 = gdf.to_crs(epsg=4326)
    
    # Create a simplified GeoDataFrame with just the necessary columns
    print("Creating simplified GeoDataFrame...")
    simplified_gdf = gdf_wgs84[['fylkesnavn', 'fylkesnummer', 'geometry']].copy()
    
    # Ensure the property names are compatible with Folium
    simplified_gdf = simplified_gdf.rename(columns={'fylkesnavn': 'name'})
    
    # Save the simplified GeoJSON
    output_file = 'static/data/norway_fylker_kartverket_wgs84.geojson'
    print(f"Saving to: {output_file}")
    simplified_gdf.to_file(output_file, driver='GeoJSON')
    
    # Verify the output file
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
            print(f"\nNumber of features in output: {len(data['features'])}")
            if len(data['features']) > 0:
                print(f"Properties of first feature: {list(data['features'][0]['properties'].keys())}")
    except Exception as e:
        print(f"Error verifying output file: {e}")
    
    print("Conversion complete!")
    return output_file

if __name__ == "__main__":
    convert_kartverket_fylker()
