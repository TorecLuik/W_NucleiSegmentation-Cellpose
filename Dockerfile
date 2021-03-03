FROM python:3.7-stretch

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

RUN pip install imageio

RUN pip install cellpose

RUN mkdir /root/.cellpose && \
    mkdir /root/.cellpose/models && \
    cd /root/.cellpose/models && \
    wget http://www.cellpose.org/models/nuclei_0 && \
    wget http://www.cellpose.org/models/nuclei_1 && \
    wget http://www.cellpose.org/models/nuclei_2 && \
    wget http://www.cellpose.org/models/nuclei_3 && \
    wget http://www.cellpose.org/models/size_nuclei_0.npy && \
    wget https://www.cellpose.org/models/cyto_0 && \
    wget https://www.cellpose.org/models/cyto_1 && \
    wget https://www.cellpose.org/models/cyto_2 && \
    wget https://www.cellpose.org/models/cyto_3 && \
    wget https://www.cellpose.org/models/size_cyto_0.npy && \
    wget https://www.cellpose.org/models/cytotorch_0 && \
    wget https://www.cellpose.org/models/cytotorch_1 && \
    wget https://www.cellpose.org/models/cytotorch_2 && \
    wget https://www.cellpose.org/models/cytotorch_3 && \
    wget https://www.cellpose.org/models/size_cytotorch_0.npy && \
    wget https://www.cellpose.org/models/nucleitorch_0 && \
    wget https://www.cellpose.org/models/nucleitorch_1 && \
    wget https://www.cellpose.org/models/nucleitorch_2 && \
    wget https://www.cellpose.org/models/nucleitorch_3 && \
    wget https://www.cellpose.org/models/size_nucleitorch_0.npy

ADD wrapper.py /app/wrapper.py

ENTRYPOINT ["python3.7","/app/wrapper.py"]
