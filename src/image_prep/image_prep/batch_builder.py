from .preprocessing_pipeline import get_hash, ImagePipeline
import os
from math import ceil
import random
import yaml
import json

random.seed(0)
class BatchBuilder:
    """
    Use this class to generate a large batch of images
    """
    
    def __init__(self, local_root="/data/"):
        self.LOCAL_ROOT = local_root
        self.batch_definition = []

    def generate_batch(self):
        """
        Generates all new images and moves into folders according to the batch definition
        Must load batch definition first.
        """
        for subset in self.batch_definition:
            in_dir, out_dir, pipeline_name, limit_n, intermediates = subset
            pipeline = ImagePipeline(local_root=self.LOCAL_ROOT, in_dir=in_dir, out_dir=out_dir)
            pipeline.load_pipeline(pipeline_name)            
            if limit_n == 0:
                limit_n = float("inf")
            
            if intermediates == True:
                intermediates = list(range(len(pipeline.tasks)))
            elif intermediates == False:
                intermediates = [len(pipeline.tasks) - 1]
            else:
                intermediates = intermediates

            orig_annot = dict()
            with open(self.LOCAL_ROOT+in_dir+'annotations.json', 'r') as f:
                for line in f.readlines():
                    orig_annot.update(json.loads(line))

            intermediate_annot = dict()
            if not os.path.exists(self.LOCAL_ROOT+pipeline.INTERMEDIATE_DIR+'annotations.json'):
                with open(self.LOCAL_ROOT+pipeline.INTERMEDIATE_DIR+'annotations.json', 'w') as f:
                    pass
            with open(self.LOCAL_ROOT+pipeline.INTERMEDIATE_DIR+'annotations.json', 'r') as f:
                for line in f.readlines():
                    intermediate_annot.update(json.loads(line))
            breakpoint()

            all_intermediates = []
            for img in self.to_process(in_dir, limit_n, len(intermediates)):
                breakpoint()
                label = orig_annot[img[:img.rfind('.')]]
                pipeline.original_img = img
                
                pipeline.generate_graph()
                pipeline.run_tasks()
                for fn in pipeline.get_file_names():
                    intermediate_annot.update({fn: label})
                all_intermediates.extend([(fn, tuple(label)) for fn in self.keep_files(pipeline, intermediates)])

            all_intermediates = [(fn, list(label)) for fn, label in list(set(all_intermediates))]
            to_keep = random.sample(all_intermediates, min(limit_n, len(all_intermediates)))
            breakpoint()
            self.move_files(to_keep, pipeline, out_dir)
            with open(self.LOCAL_ROOT+pipeline.INTERMEDIATE_DIR+'annotations.json', 'w') as f:
                for file_name, label in intermediate_annot.items():
                    f.write(json.dumps({file_name: label}) + '\n')       

    def move_files(self, to_keep, pipeline, out_dir):
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
        if not os.path.exists(self.LOCAL_ROOT + out_dir + 'annotations.json'):
            with open(self.LOCAL_ROOT + out_dir + 'annotations.json', 'w') as f_create:
                pass

        out_dir_annots = dict()
        with open(self.LOCAL_ROOT+out_dir+'annotations.json', 'r') as f:
            for line in f.readlines():
                out_dir_annots.update(json.loads(line))

        for file_name, label in to_keep:
            os.rename(
                pipeline.LOCAL_ROOT + pipeline.INTERMEDIATE_DIR + file_name,
                self.LOCAL_ROOT + out_dir + file_name,
            )
            out_dir_annots.update({file_name[:file_name.rfind('.')]: label})

        out_dir_fns = [fn[:fn.rfind('.')] for fn in os.listdir(self.LOCAL_ROOT+out_dir)]
        for key in out_dir_annots:
            if key not in out_dir_fns:
                del out_dir_annots[key]
        with open(self.LOCAL_ROOT+out_dir+'annotations.json', 'w') as f:
            for file_name, label in out_dir_annots.items():
                f.write(json.dumps({file_name: label}) + '\n')            

    def to_process(self, in_dir, limit_n, n_intermediates):
        """
        Takes random sample of images to avoid generating more than needed
        """
        filenames = [fn for fn in os.listdir(self.LOCAL_ROOT + in_dir) if fn!='annotations.json']
        if limit_n == float("inf"):
            n = float("inf")
        else:
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
