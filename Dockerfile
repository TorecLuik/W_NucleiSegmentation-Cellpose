FROM python:3.7-bullseye

# ------------------------------------------------------------------------------
# Install Cytomine python client
RUN git clone https://github.com/cytomine-uliege/Cytomine-python-client.git && \
    cd /Cytomine-python-client && git checkout tags/v2.7.3 && pip install . && \
    rm -r /Cytomine-python-client

# ------------------------------------------------------------------------------
# Install BIAFLOWS utilities (annotation exporter, compute metrics, helpers,...)
RUN apt-get update && apt-get install libgeos-dev -y && apt-get clean
RUN git clone https://github.com/Neubias-WG5/biaflows-utilities.git && \
    cd /biaflows-utilities/ && git checkout tags/v0.9.2 && pip install .

# install utilities binaries
RUN chmod +x /biaflows-utilities/bin/*
RUN cp /biaflows-utilities/bin/* /usr/bin/ && \
    rm -r /biaflows-utilities

# ------------------------------------------------------------------------------
RUN pip install imageio==2.9.0
RUN pip install cellpose==0.7.2
RUN pip install numpy==1.19.4
RUN pip install numba==0.50.1

# Create cellpose models directory
RUN mkdir -p /opt/cellpose/models

# Copy local models instead of downloading
COPY models/ /opt/cellpose/models/

# Set local models path
# This is needed to avoid downloading the models from the internet
# and to not use home dir for storing models
ENV CELLPOSE_LOCAL_MODELS_PATH=/opt/cellpose/models

ADD wrapper.py /app/wrapper.py
# for running the wrapper locally
ADD descriptor.json /app/descriptor.json

ENTRYPOINT ["python3.7","/app/wrapper.py"]
