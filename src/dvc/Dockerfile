FROM python:3.8 AS base

RUN wget https://dvc.org/deb/dvc.list -O /etc/apt/sources.list.d/dvc.list &&\
    wget -qO - https://dvc.org/deb/iterative.asc | gpg --dearmor > packages.iterative.gpg &&\
    install -o root -g root -m 644 packages.iterative.gpg /etc/apt/trusted.gpg.d/ &&\
    rm -f packages.iterative.gpg &&\
    apt update &&\
    apt install -y dvc

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.asc] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list &&\ 
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | tee /usr/share/keyrings/cloud.google.asc &&\ 
    apt-get update -y && apt-get install google-cloud-sdk -y
      
WORKDIR /snapnutrition
CMD ["gcloud", "auth", "activate-service-account", "--key-file=/secrets/data-service-account.json"]