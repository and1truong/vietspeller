# Vietspeller

Tiny, offline Vietnamese spelling detection and minimal-edit correction, with foreign-name preservation, reproducible datasets, and CPU benchmarks.

**Status:** research scaffold, Phase 1–2. No detector, trained weights, correction API, or measured quality/latency results yet. The executable component currently validates dataset contracts and common split leakage.

## Bắt đầu ở đây

1. Đọc [problem definition](docs/problem-definition.md), đặc biệt ranh giới spelling và chính sách abstain.
2. Đọc [E001](experiments/E001-baseline-feasibility.md). Ghi dự đoán trước khi chạy model.
3. Kiểm tra [data contract](docs/data-contract.md) và các ví dụ minh họa.
4. Thu thập dữ liệu có provenance; chỉ chuyển sang baseline khi data gate đạt.

Python 3.11 trở lên; scaffold không cần third-party runtime dependencies. Chạy từ repo root:

```sh
PYTHONPATH=src python -m vietspeller.cli validate data/examples/illustrative.jsonl
PYTHONPATH=src python -m unittest discover -s tests -v
```

Có thể cài package bằng `python -m pip install -e .`, rồi dùng `vietspeller validate PATH...`. Truyền tất cả split files cùng một lần để kiểm tra leakage giữa các file.

## Tài liệu

- [Problem definition và output contract](docs/problem-definition.md)
- [Dataset contract và provenance](docs/data-contract.md)
- [Benchmark protocol](docs/benchmark.md)
- [Architectures và nguồn nghiên cứu](docs/research.md)
- [Roadmap và acceptance gates](docs/roadmap.md)
- [E001: precision-constrained baseline](experiments/E001-baseline-feasibility.md)
- [Mẫu experiment report](experiments/report-template.md)

## Cách làm việc

Mentor giúp đặt giả thuyết, review và thiết kế ablation. Người học triển khai detector, chạy thí nghiệm và giải thích quyết định. Routine tooling có thể được cung cấp trực tiếp. Không chọn neural architecture trước khi baseline và error analysis chỉ ra nhu cầu.

Model size tính cả weights, dictionary, tokenizer và bảng phụ trợ. Runtime disk size và process RAM đo riêng. Không cần LLM tại inference; LLM data generation chưa được tích hợp.

Fixture minh họa không phải authentic benchmark và không được dùng để công bố quality. Repo chưa chọn license cho code; quyền sử dụng từng nguồn dữ liệu phải được kiểm tra riêng.
