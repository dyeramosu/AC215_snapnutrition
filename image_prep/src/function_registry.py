import skimage
from functools import partial

function_registry = {
    "grayscale": {
        "func": skimage.color.rgb2gray,
    },
    "equalize_hist": {
        "func": skimage.exposure.equalize_hist,
        "params": {"nbins": {"type": int, "default": 256, "range": (0, 1000)}},
    },
    "equalize_adapthist": {
        "func": skimage.exposure.equalize_adapthist,
        "params": {
            "nbins": {"type": int, "default": 256, "range": (0, 1000)},
            "kernel_size": {"type": int, "default": 8, "range": (0, 100)},
        },
    },
    "rotate": {
        "func": skimage.transform.rotate,
        "params": {
            "resize": {"type": bool, "default": True},
            "angle": {"type": float, "default": 180, "range": (0, 360)},
        },
    },
    "rescale": {
        "func": skimage.transform.rescale,
        "params": {"scale": {"type": float, "default": 0.5, "range": (0, 10)}},
    },
    "swirl": {
        "func": skimage.transform.swirl,
        "params": {
            "strength": {"type": float, "default": 1, "range": (0, 5)},
            "radius": {"type": float, "default": 100, "range": (0, 1000)},
        },
    },
    "filter_gaussian": {
        "func": skimage.filters.gaussian,
        "params": {"sigma": {"type": float, "default": 1, "range": (0, 10)}},
    },
    "filter_butterworth": {
        "func": skimage.filters.butterworth,
        "params": {
            "cutoff_frequency_ratio": {
                "type": float,
                "default": 0.005,
                "range": (0, 5),
            },
            "high_pass": {"type": bool, "default": True},
        },
    },
    "filter_sobel": {
        "func": skimage.filters.sobel,
        "params": {},
    },
    "rank_equalize": {
        "func": partial(
            skimage.filters.rank.equalize, footprint=skimage.morphology.disk(50)
        ),
        "params": {},
    },
    "rank_entropy": {
        "func": skimage.filters.rank.entropy,
        "params": {},
    },
}


# skimage.filters.rank.equalize
# skimage.filters.rank.entropy
# binarization otsu
# inversion
# resizing
# gaussian filter
# median filter
# sobel filter
# add noise (salt and pepper, gaussian)
