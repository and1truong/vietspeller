"""Measured warm CPU timings and process peak RSS; no fabricated cold timings."""

import math
from pathlib import Path
import platform
import sys
import time

from . import baseline, data, text


def benchmark(model, sentences: list[tuple[str, str]], artifact: Path, warmup: int, repeat: int) -> dict:
    if not sentences or warmup < 0 or repeat < 1:
        raise ValueError("benchmark needs sentences, nonnegative warmup and positive repeat")
    for i in range(warmup):
        model.check(*sentences[i % len(sentences)])
    timings = []
    for i in range(repeat):
        sentence, profile = sentences[i % len(sentences)]
        started = time.perf_counter_ns()
        model.check(sentence, profile)
        timings.append((time.perf_counter_ns()-started) / 1e6)
    ordered = sorted(timings)
    p50 = ordered[max(0, math.ceil(.5*len(ordered))-1)]
    p95 = ordered[max(0, math.ceil(.95*len(ordered))-1)]
    peak_rss = None
    try:
        import resource
        peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        peak_rss *= 1 if sys.platform == "darwin" else 1024
    except ImportError:
        pass
    modules = [Path(__file__).with_name("__init__.py"), Path(baseline.__file__), Path(data.__file__), Path(text.__file__)]
    source_bytes = sum(p.stat().st_size for p in modules)
    cpu = platform.processor()
    if Path("/proc/cpuinfo").exists():
        cpu = next((line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                    if line.startswith("model name")), cpu)
    return {"calls": repeat, "warmup_calls": warmup, "batch_size": 1, "execution": "single Python thread",
            "warm_latency_ms": {"p50": p50, "p95": p95},
            "serial_throughput_sentences_per_second": 1000*repeat/sum(timings) if sum(timings) else None,
            "input_codepoint_lengths": sorted({len(s) for s, _ in sentences}),
            "process_peak_rss_bytes": peak_rss, "artifact_bytes": artifact.stat().st_size,
            "inference_python_source_bytes": source_bytes,
            "inference_bundle_bytes": source_bytes + artifact.stat().st_size,
            "size_excludes": ["Python interpreter", "standard library", "evaluation and CLI tooling"],
            "cpu": cpu, "os": platform.platform(), "python": platform.python_version(),
            "cold_process_latency_ms": None,
            "limitations": ["Peak RSS includes data loading and the complete CLI process; run in a fresh process.",
                            "Local environment timing only; no CPU affinity or frequency control.",
                            "Lexicon scan is O(vocabulary_size * token_length^2); bootstrap timings do not extrapolate.",
                            "No length-bucket or baseline-runtime-only RAM measurements yet."]}
