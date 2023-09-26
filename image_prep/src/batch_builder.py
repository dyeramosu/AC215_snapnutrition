from .preprocessing_pipeline import get_hash, ImagePipeline
import os
from math import ceil
import random
import yaml


random.seed(0)
class BatchBuilder:
    """
    Use this class to generate a large batch of images
    """
    
    def __init__(self, local_root="data/"):
        self.LOCAL_ROOT = local_root
        self.batch_definition = []

    def generate_batch(self):
        """
        Generates all new images and moves into folders according to the batch definition
        Must load batch definition first.
        """
        for subset in self.batch_definition:
            in_dir, out_dir, pipeline_name, limit_n, intermediates = subset
            pipeline = ImagePipeline(local_root=self.LOCAL_ROOT, in_dir=in_dir)
            pipeline.load_pipeline(pipeline_name)

            if intermediates == True:
                intermediates = list(range(len(pipeline.tasks)))
            elif intermediates == False:
                intermediates = [len(pipeline.tasks) - 1]

            all_intermediates = []
            for img in self.to_process(in_dir, limit_n, len(intermediates)):
                pipeline.original_img = img
                pipeline.generate_graph()
                pipeline.run_tasks()
                all_intermediates.extend(self.keep_files(pipeline, intermediates))

            all_intermediates = list(set(all_intermediates))
            to_keep = random.sample(all_intermediates, min(limit_n, len(all_intermediates)))
            self.move_files(to_keep, pipeline, in_dir, out_dir)

    def move_files(self, to_keep, pipeline, in_dir, out_dir):
        """
        Move files from pipeline output directory to its destination

        :params: 
        :to_keep: list of file names to move
        :pipeline: the pipeline that was used to generate the images
        :in_dir: current directory they're contained in, defined by pipeline
        :out_dir: directory to move files to
        """
        if not os.path.isdir(self.LOCAL_ROOT + out_dir):
            os.makedirs(self.LOCAL_ROOT + out_dir)
        breakpoint()
        for file_name in to_keep:
            os.rename(
                pipeline.LOCAL_ROOT + pipeline.OUT_DIR + file_name,
                self.LOCAL_ROOT + out_dir + file_name,
            )

    def to_process(self, in_dir, limit_n, n_intermediates):
        """
        Takes random sample of images to avoid generating more than needed
        """
        filenames = os.listdir(self.LOCAL_ROOT + in_dir)
        n = ceil(limit_n / n_intermediates)
        return random.sample(filenames, min(n, len(filenames)))

    def keep_files(self, pipeline, intermediates):
        """
        Returns a list of pipeline-generated filenames corresponding to the
        defined intermediates
        """
        # identify filenames corresponding to intermediates
        all_file_names = pipeline.get_file_names()
        keep = [
            all_file_names[i] for i in range(len(all_file_names)) if i in intermediates
        ]
        return keep

    def save_batch_definition(self, name):
        """
        Saves batch definition as yaml into ./batch_definitions/
        """
        if not os.path.exists("./batch_definitions/"):
            os.mkdir("./batch_definitions/")
        with open("./batch_definitions/" + name, "w") as f:
            f.write(yaml.dump({"subsets": [list(s) for s in self.batch_definition]}))

    def load_batch_definition(self, name):
        """
        Load yaml file definition from ./batch_definitions/
        """
        with open("./batch_definitions/" + name, "r") as f:
            self.batch_definition = yaml.load(f.read(), yaml.Loader)["subsets"]

    def add_subset(self, input_dir, out_dir, pipeline, n, intermediates):
        """
        Add a subset to current batch_definition

        :params: 
        :input_dir: directory containing raw images
        :out_dir: directory to move processed images into
        :pipeline: an ImagePipeline to apply to images in input_dir
        :n: hard limit on number of images to move into out_dir
        :intermediates: list of task indices of intermediates to keep, 
            use True for all, False for just the final image
        """
        self.batch_definition.append((input_dir, out_dir, pipeline, n, intermediates))

    def remove_subset(self, i):
        """
        Removes subset from batch definition

        :i: index of subset to remove
        """
        self.batch_definition.pop(i)
