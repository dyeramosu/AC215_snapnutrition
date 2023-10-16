from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = [
    "wandb==0.15.11", 
    "google-cloud-storage",
    "pyyaml" 
]

setup(
    name="snapnutrition-model-trainer",
    version="0.0.1",
    install_requires=REQUIRED_PACKAGES,
    # use findpackages() to include all subdirectories with __init__.py
    packages=find_packages(),
    description="SnapNutrition Trainer Application",
    # "" indicates the *.yml files from all source directories should be 
    # captured as data files in the package
    package_data={"": ["*.yml"]}
)
