FROM python:3.8 AS base

RUN wget https://dvc.org/deb/dvc.list -O /etc/apt/sources.list.d/dvc.list &&\
    wget -qO - https://dvc.org/deb/iterative.asc | gpg --dearmor > packages.iterative.gpg &&\
    install -o root -g root -m 644 packages.iterative.gpg /etc/apt/trusted.gpg.d/ &&\
    rm -f packages.iterative.gpg &&\
    apt update &&\
    apt install dvc

WORKDIR /snapnutrition