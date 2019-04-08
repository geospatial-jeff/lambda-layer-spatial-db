import pywraps2 as s2
from ZODB import FileStorage, DB
from BTrees.OOBTree import OOBTree
import transaction

class Database(object):

    @classmethod
    def load(cls, path):
        storage = FileStorage.FileStorage(path)
        db = DB(storage)
        connection = db.open()
        root = connection.root
        if not hasattr(root, "features"):
            root.features = OOBTree()
            transaction.commit()
        return cls(db, connection, root)


    def __init__(self, db, conn, root):
        self.db = db
        self.conn = conn
        self.root = root
        self.min_res = 11
        self.max_res = 14
        self.limit = 100
        self.unique_id = 'NAME'

    def cover_region(self, feature):
        # Cover a feature's extent with S2 cells
        xcoords = [x[0] for x in feature['geometry']['coordinates'][0]]
        ycoords = [y[1] for y in feature['geometry']['coordinates'][0]]
        rect = s2.S2LatLngRect(s2.S2LatLng.FromDegrees(min(ycoords), min(xcoords)),
                               s2.S2LatLng.FromDegrees(max(ycoords), max(xcoords)))
        coverer = s2.S2RegionCoverer()
        coverer.set_max_cells(self.limit)
        coverer.set_min_level(self.min_res)
        coverer.set_max_level(self.max_res)
        ids = coverer.GetCovering(rect)
        return ids

    def load_features(self, feature_collection):
        for feat in feature_collection['features']:
            self._load_feature(feat)
        transaction.commit()

    def _load_feature(self, feature):
        ids = self.cover_region(feature)
        for id in ids:
            self.root.features[hash(id)] = feature['properties']

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
                if resp[1][self.unique_id] not in cities:
                    valid.append(resp[1])
                    cities.append(resp[1][self.unique_id])

        return valid

    def close(self):
        self.conn.close()