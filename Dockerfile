FROM python:3.11-slim-bookworm

RUN adduser --uid 1001 --disabled-password --gecos '' ipstack

USER ipstack
WORKDIR /home/ipstack

RUN python3 -m venv venv && \
    venv/bin/python -m pip install --upgrade pip setuptools wheel && \
    venv/bin/pip install requests && \
    venv/bin/pip cache purge

COPY ipstack_latlong.py .

ENTRYPOINT ["venv/bin/python", "ipstack_latlong.py"]
CMD ["--help"]
