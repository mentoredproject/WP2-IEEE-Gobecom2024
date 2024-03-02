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
COPY --from=builder /app/adaptive_padding/run_nearest_padding.py .
COPY --from=builder /app/adaptive_padding/prepare_features.py .
COPY --from=builder /app/adaptive_padding/padding_strategies_evaluation.py .
COPY --from=builder /app/adaptive_padding/make_plots.py .
COPY --from=builder /app/adaptive_padding/compute_byte_overhead.py .
COPY --from=builder /app/adaptive_padding/padding/nearest /app/adaptive_padding/padding/nearest

RUN pip3 install *.whl
RUN rm *.whl

# install Julia
RUN apt update && apt install -y wget
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.10/julia-1.10.2-linux-x86_64.tar.gz
RUN tar zxvf julia-1.10.2-linux-x86_64.tar.gz -C /opt
RUN rm julia-1.10.2-linux-x86_64.tar.gz

ENV PATH "${PATH}:/opt/julia-1.10.2/bin"

RUN julia adaptive_padding/padding/nearest/install_dependencies.jl

CMD ["bash"]