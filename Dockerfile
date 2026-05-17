FROM python:3.11-slim

LABEL maintainer="Agent Team <agent@example.com>"
LABEL description="Agent Perpetual System - 永续循环自进化运行系统"
LABEL version="2.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]" \
    && pip cache purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY src/ ./src/
COPY layer_8_testing_verification/ ./layer_8_testing_verification/

RUN python -c "import sys; print(f'Python {sys.version}')" \
    && python -m pytest --collect-only layer_8_testing_verification/ \
    && python -c "from src.agent_perpetual_system_complete import __version__; print(f'Agent Perpetual System installed')"

EXPOSE 8000 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

USER 1001

ENTRYPOINT ["python", "-m"]
CMD ["uvicorn", "src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation:app", "--host", "0.0.0.0", "--port", "8000"]
