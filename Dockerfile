FROM python:3.12-alpine

WORKDIR /workspace

RUN pip install --no-cache-dir jsonschema==4.26.0 pytest==9.1.1

COPY . /workspace

ENV PYTHONPATH=/workspace/src

CMD ["sh", "-c", "python -m pytest && python src/data2dsl_contract_v0/validate.py --self-test"]
