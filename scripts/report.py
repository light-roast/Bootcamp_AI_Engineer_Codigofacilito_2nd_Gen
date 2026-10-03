"""Reporte de llamadas al LLM a partir de logs/llm_calls.jsonl.

Uso:
    uv run scripts/report.py [ruta/al/archivo.jsonl]
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

DEFAULT_PATH = Path("logs/llm_calls.jsonl")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = Path(argv[0]) if argv else DEFAULT_PATH

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        print(f"No se encontró el archivo: {path}")
        return 1

    events = [json.loads(line) for line in lines if line.strip()]
    if not events:
        print(f"El archivo está vacío: {path}")
        return 0

    print(f"Llamadas registradas: {len(events)}")

    total_cost = sum(event["cost_usd"] for event in events)
    successful_latencies = [
        event["latency_ms"] for event in events if event["success"]
    ]
    fallback_count = sum(event["fallback"] for event in events)
    fallback_percent = fallback_count / len(events) * 100
    provider_counts = Counter(event["provider"] for event in events)

    print(f"Costo total: ${total_cost:.6f} USD")
    if len(successful_latencies) >= 2:
        percentiles = statistics.quantiles(
            successful_latencies, n=100, method="inclusive"
        )
        print(f"Latencia p50: {percentiles[49]:.2f} ms")
        print(f"Latencia p95: {percentiles[94]:.2f} ms")
    else:
        print("Latencia p50: N/D (se requieren al menos dos llamadas exitosas)")
        print("Latencia p95: N/D (se requieren al menos dos llamadas exitosas)")
    print(f"Llamadas con fallback: {fallback_percent:.1f}%")
    print("Llamadas por proveedor:")
    for provider, count in sorted(provider_counts.items()):
        print(f"  {provider}: {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
