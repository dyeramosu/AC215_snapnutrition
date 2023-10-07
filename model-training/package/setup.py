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
    packages=find_packages(),
    description="SnapNutrition Trainer Application",
    package_data={"": ["*.yml"]}
)
