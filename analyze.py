import math
from scipy import stats

import numpy as np
from shapely.geometry import Polygon
import pyproj
from tqdm import tqdm


# Average cell areas (square meters)
s2_cell_areas = {
    0: 85011012190000,
    1: 21252753050000,
    2: 5313188260000,
    3: 1328297070000,
    4: 332074270000,
    5: 83018570000,
    6: 20754640000,
    7: 5188660000,
    8: 1297170000,
    9: 324290000,
    10: 81070000,
    11: 20270000,
    12: 5070000,
    13: 1270000,
    14: 320000,
    15: 79172,
    16: 19793,
    17: 4948,
    18: 1237,
    19: 309,
    20: 77,
    21: 19,
    22: 4,
    23: 1,
}

out_epsg = pyproj.Proj('+proj=moll +lon_0=0')


def choose_res(feature_collection, optimize='size'):

    areas = []
    perimeters = []
    circularities = []

    # Reproject
    print("Analyzing Features")
    for feat in tqdm(feature_collection['features']):
        # Get centroid in 4326
        # Use utm to parse epsg code
        # Reproject
        proj_coords = [list(out_epsg(*ring)) for ring in feat['geometry']['coordinates'][0]]
        geom_proj = Polygon(proj_coords)
        area = geom_proj.area
        perimeter = geom_proj.length
        # Calculate circularity with Polsby-Popper
        circularity = (4* math.pi * area) / perimeter**2
        areas.append(area)
        perimeters.append(perimeter)
        circularities.append(circularity)


    area_stats = stats.describe(areas)
    min_thresh = None
    mean_thresh = None
    max_thresh = None

    # Using the 10th/90th area percentiles.  This will create size/accuracy optimizations in the presence of outliers
    # or a heavily skewed distribution.  Won't have any effect on a normal distribution (size and accuracy will both
    # generate the same recommendations).
    # TODO: Improve this algorithm
    for res in s2_cell_areas:
        if optimize == 'size':
            min_diff = s2_cell_areas[res] - np.percentile(areas, 10)
        else:
            min_diff = s2_cell_areas[res] - area_stats.minmax[0]

        mean_diff = s2_cell_areas[res] - area_stats.mean

        if optimize == 'accuracy':
            max_diff = s2_cell_areas[res] - np.percentile(areas, 90)
        else:
            max_diff = s2_cell_areas[res] - area_stats.minmax[1]

        if min_diff < 0 and not min_thresh:
            min_thresh = res
        if mean_diff < 0 and not mean_thresh:
            mean_thresh = res
        if max_diff < 0 and not max_thresh:
            max_thresh = res

    print("Recommended minimum resolution: {}".format(min_thresh))
    print("Recommended maximum resolution: {}".format(max_thresh))
    print("")
    print("Vector Statistics:")
    print("AREA")
    print(area_stats)
    print("")
    print("PERIMETER")
    print(stats.describe(perimeters))
    print("")
    print("CIRCULARITY")
    print(stats.describe(circularities))