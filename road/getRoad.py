import geopandas as gpd
from sqlalchemy import create_engine

def get_road_from_db(ref=None, iso_1=None):
    db_connection = "postgresql://postgres:3004@localhost:4321/itsp"
    try:
        engine = create_engine(db_connection)
        query = """
        SELECT ref, "ISO_1", geometry
        FROM roads_with_iso
        WHERE 1=1
        """
        if iso_1:
            query += f" AND \"ISO_1\" = '{iso_1}'"
        if ref:
            query += f" AND ref = '{ref}'"

        roads = gpd.read_postgis(query, con=engine, geom_col="geometry")
        return roads
    except Exception as e:
        print(f"Error retrieving roads from the database: {e}")
        return gpd.GeoDataFrame()