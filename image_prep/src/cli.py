from .batch_builder import BatchBuilder
import argparse
import sys


def cli():
    """
    Pass a list of batch_definition filenames through the command line.
    Must be in the 'batch_definitions' folder
    """
    for batch_def in sys.argv[1:]:
        x = BatchBuilder()
        x.load_batch_definition(batch_def)
        x.generate_batch()
