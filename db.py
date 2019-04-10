import sys
from tqdm import tqdm

import pywraps2 as s2
from ZODB import FileStorage, DB
from BTrees.OOBTree import OOBTree
import transaction

class DatabaseConfig(object):

    min_res = 10
    max_res = 12
    limit = 100
    unique_id = 'NAME'

class Database(object):

    @classmethod
    def load(cls, path, config, read_only=False):
        storage = FileStorage.FileStorage(path, read_only=read_only)
        db = DB(storage)
        connection = db.open()
        root = connection.root
        # Create a root if doesn't exist
        if not hasattr(root, "features"):
            root.features = OOBTree()
            transaction.commit()
        return cls(db, connection, root, config)

    @staticmethod
    def load_config(config):
        expected = ['min_res', 'max_res', 'limit', 'unique_id']
        for item in expected:
            if not hasattr(config, item):
                raise ValueError("Configuration is missing the required {} attribute".format(item))
        return config


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def __init__(self, db, conn, root, config):
        self.db = db
        self.conn = conn
        self.root = root
        self.config = self.load_config(config)

    def cover_region(self, feature):
        # Cover a feature's extent with S2 cells
        xcoords = [x[0] for x in feature['geometry']['coordinates'][0]]
        ycoords = [y[1] for y in feature['geometry']['coordinates'][0]]
        rect = s2.S2LatLngRect(s2.S2LatLng.FromDegrees(min(ycoords), min(xcoords)),
                               s2.S2LatLng.FromDegrees(max(ycoords), max(xcoords)))
        coverer = s2.S2RegionCoverer()
        coverer.set_max_cells(self.config.limit)
        coverer.set_min_level(self.config.min_res)
        coverer.set_max_level(self.config.max_res)
        ids = coverer.GetCovering(rect)
        return ids

    def load_features(self, feature_collection):
        cellcount = 0
        print("Loading features")
        for feat in tqdm(feature_collection['features']):
            count = self._load_feature(feat)
            cellcount += count
        print("Committing transaction")
        transaction.commit()

        print(f"Loaded {cellcount} cells across {len(feature_collection['features'])} ({cellcount/len(feature_collection['features'])} cells per polygon)")


    def _load_feature(self, feature):
        ids = self.cover_region(feature)
        for id in ids:
            self.root.features[hash(id)] = feature['properties']
        return len(ids)

    def spatial_query(self, geoj):
        region = self.cover_region(geoj)
        db_feats = self.root()['features']

        valid = []
        cities = []

        for cell in region:
            rmin = hash(cell.range_min())
            rmax = hash(cell.range_max())
            response = list(db_feats.items(min=rmin, max=rmax))
            for resp in response:
                if resp[1][self.config.unique_id] not in cities:
                    valid.append(resp[1])
                    cities.append(resp[1][self.config.unique_id])
        return valid

    def close(self):
        self.conn.close()