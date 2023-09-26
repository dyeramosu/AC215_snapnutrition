import os
import yaml

from luigi.format import Nop
from luigi import Task, Parameter, DictParameter, build

from .function_registry import *
from typing import Union
import hashlib
import numpy as np

from .task import TargetOutput, Requires, Requirement

def hash_str(some_val: Union[str, bytes], salt: Union[str, bytes] = "") -> bytes:
    """Converts strings to hash digest

    See: https://en.wikipedia.org/wiki/Salt_(cryptography)

    :param some_val: thing to hash, can be str or bytes
    :param salt: Add randomness to the hashing, can be str or bytes
    :return: sha256 hash digest of some_val with salt, type bytes
    """
    if type(some_val) == str:
        some_val = some_val.encode()
    if type(salt) == str:
        salt = salt.encode()

    m = hashlib.sha256()
    m.update(salt)
    m.update(some_val)
    return m.digest()


def get_hash(parent, process, kwargs):
    """
    Returns hash of input filename, current task, and params. This becomes the filename to output.
    """
    return hash_str(
        process + str(sorted([(key, val) for key, val in kwargs.items()])), salt=parent
    ).hex()[:25]


class SaltedOutput(TargetOutput):
    """
    Class to auto-generate salted filename when written to.
    """
    def __call__(self, task):
        i = task.file_name.rfind("/")
        j = task.file_name.rfind(".")

        fn, ext = task.file_name[i+1:j], task.file_name[j:]
        breakpoint()
        unique_string = get_hash(fn, task.image_process, task.kwargs)

        return self.target_class(
            task.OUT_DIR + unique_string + ext, **self.target_kwargs
        )


class InitialImageTask(Task):
    """
    Luigi task to apply the first function to the original image.
    """
    image_process = Parameter()
    kwargs = DictParameter({})

    file_name = Parameter()
    OUT_DIR = Parameter()

    output = SaltedOutput()

    def run(self):
        func = function_registry[self.image_process]["func"]
        img = skimage.io.imread(self.file_name)
        img = func(img, **self.kwargs)
        breakpoint()
        skimage.io.imsave(self.output().path, (img * 255).astype(np.uint8))


class ImagePipeline:
    """
    Applies a series of image processing functions to a raw image
    """

    def __init__(
        self,
        original_img="choose a file",
        local_root="data/",
        in_dir="raw/",
        out_dir="processed/all/",
    ):
        self.LOCAL_ROOT = local_root
        self.IN_DIR = in_dir
        self.OUT_DIR = out_dir
        self.original_img = original_img

        self.tasks = []
        self.luigi_graph = []

        if not os.path.exists(self.LOCAL_ROOT):
            os.makedirs(self.LOCAL_ROOT)
        if not os.path.exists(self.LOCAL_ROOT + self.IN_DIR):
            os.makedirs(self.LOCAL_ROOT + self.IN_DIR)
        if not os.path.exists(self.LOCAL_ROOT + self.OUT_DIR):
            os.makedirs(self.LOCAL_ROOT + self.OUT_DIR)

    def add_task(self, func: str, params = {}):
        """
        Adds a task

        :params:
        :func: a string corresponding with some function in function_registry.py
        :params: all keyword args to pass to func in a dictionary
        """
        self.tasks.append({"func": func, "params": params})

    def remove_task(self):
        """
        Removes the last task from the current task list
        """
        if len(self.tasks) > 0:
            self.tasks.pop(-1)

    def generate_graph(self):
        """
        Generates luigi graph according to self.original_img and self.pipeline
        """

        if len(self.tasks) >= 1:
            self.luigi_graph = []
            kwargs = dict(
                file_name=self.LOCAL_ROOT + self.IN_DIR + self.original_img,
                image_process=self.tasks[0]["func"],
                kwargs=self.tasks[0]["params"],
                OUT_DIR=self.LOCAL_ROOT + self.OUT_DIR,
            )
            self.luigi_graph.append(InitialImageTask(**kwargs))

            for i in range(1, len(self.tasks)):
                self.luigi_graph.append(
                    self.generate_next_task(
                        prev_task=self.luigi_graph[i - 1],
                        func=self.tasks[i]["func"],
                        params=self.tasks[i]["params"],
                    )
                )

    def run_tasks(self):
        """
        Builds the luigi graph and generates all processed images.
        """

        build([self.luigi_graph[-1]], local_scheduler=True)

    def generate_next_task(self, prev_task, func, params):
        """
        Function to add the next task to the luigi pipeline
        """
        OUT_DIR = self.OUT_DIR

        class ImageTask(InitialImageTask):
            file_name = prev_task.output().path

            def requires(self):
                return prev_task

        return ImageTask(
            image_process=func, kwargs=params, OUT_DIR=self.LOCAL_ROOT + self.OUT_DIR
        )

    def save_pipeline(self, name):
        """
        Saves pipeline definition into ./pipelines/

        :params:
        :name: Name to save pipeline as.
        """

        if not os.path.exists("./pipelines/"):
            os.mkdir("./pipelines/")
        with open("./pipelines/" + name, "w") as f:
            f.write(yaml.dump({"tasks": self.tasks}))

    def load_pipeline(self, name):
        """
        Loads pipeline from its yaml definition into self.pipeline
        """
        with open("./pipelines/" + name, "r") as f:
            self.tasks = yaml.load(f.read(), yaml.Loader)["tasks"]
        self.luigi_graph = []

    def get_file_names(self):
        """
        Returns all filenames that the current pipeline will generate when run
        """
        
        file_names = []
        prev = self.LOCAL_ROOT + self.IN_DIR + self.original_img
        for task in self.tasks:
            i = prev.rfind("/")
            j = prev.rfind(".")

            fn, ext = prev[i+1:j], prev[j:]
            breakpoint()
            unique_string = get_hash(fn, task["func"], task["params"])
            prev = self.LOCAL_ROOT + self.OUT_DIR + unique_string + ext
            file_names.append(prev)
        file_names = [
            fn.replace(self.LOCAL_ROOT + self.OUT_DIR, "") for fn in file_names
        ]
        return file_names
