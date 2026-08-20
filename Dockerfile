FROM python:3.12-alpine@sha256:d8c55e9b897e68fa7bb8e37682337772656910cb13c38b25be24b3353ae41088

WORKDIR /workspace

RUN pip install --no-cache-dir jsonschema==4.26.0 pytest==9.1.1

COPY . /workspace

ENV PYTHONPATH=/workspace/src

CMD ["sh", "-c", "python -m pytest && python src/data2dsl_contract_v0/validate.py --self-test"]
