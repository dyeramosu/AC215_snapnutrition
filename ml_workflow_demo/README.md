# Overview
The purpose of this folder is to demonstrate the ml workflow tutorial presented in class. This tutorial teaches some basics of Kubeflow and Vertex AI Pipelines. 

*Adopted from the following GitHub Repository developed and provided by Shivas Javaram https://github.com/dlops-io/ml-workflow/*

## Setup Environments

### Create a Service Account
* Screenshot of creating the service account called `ml-workflow`: 
<img src="screencaps/service_account_creation.png"  width="700">

### Create Bucket
* Screenshot of creating the storage bucket `snapnutrition-ml-workflow-demo`
<img src="screencaps/bucket_creation.png"  width="700">

## Data Collector Container

### Edit Data Collector Docker Shell Script
* Screenshot of tailored shell script: 
<img src="screencaps/data_collector_docker_shell.png"  width="700">

### Build Data Collector Docker Container
* Screenshot of completed data collection:
<img src="screencaps/test_data_collector.png"  width="700">

* Screenshot of raw zip file uploaded to bucket:
<img src="screencaps/raw_zip.png"  width="700">

## Running Workflow Pipeline

### Edit Workflow Docker Shell Script
* Screenshot of tailored shell script: 
<img src="screencaps/workflow_docker_shell.png"  width="700">

### Run Data Collector Pipeline
* Screenshot of running data collection pipeline:
<img src="screencaps/data_collector_pipeline_complete.png"  width="700">

* Screenshot of running workflow pipeline:
<img src="screencaps/ml_pipeline_initial.png"  width="700">
