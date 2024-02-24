FROM python:3.11 AS builder

WORKDIR /app

COPY adaptive_padding/ adaptive_padding/
COPY poetry.lock .
COPY pyproject.toml .
COPY README.md .

RUN apt update && apt install python3-poetry -y
RUN poetry install
RUN poetry build --format wheel

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /app/dist/*.whl .
COPY --from=builder /app/adaptive_padding/run_proposal_padding.py .
COPY --from=builder /app/adaptive_padding/run_existing_padding.py .
COPY --from=builder /app/adaptive_padding/prepare_features.py .
COPY --from=builder /app/adaptive_padding/padding_strategies_evaluation.py .
COPY --from=builder /app/adaptive_padding/make_plots.py .
COPY --from=builder /app/adaptive_padding/compute_byte_overhead.py .

RUN pip3 install *.whl
RUN rm *.whl

CMD ["bash"]