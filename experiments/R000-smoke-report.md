# R000 — Rules baseline functional diagnostic

Status: complete, 2026-10-20. **Không phải E001 hoặc independent quality benchmark.**

## Câu hỏi và setup

Kiểm tra inference, Unicode offsets, evaluator và CPU harness có chạy end-to-end, đồng thời lưu các failure cases của baseline. Không chọn threshold/model dựa trên scores này.

Nguồn: 22 project-authored illustrative records, 13 gold edits, 10 clean sentences, 18 valid entity spans, 2 genuine errors trong entity surfaces. Seed vocabulary 138 syllables và 18 protected phrases/terms, được viết cùng diagnostic examples; không độc lập với evaluation text. Chưa có train/validation/independent test hoặc annotation agreement audit.

Code/data/artifact SHA-256 trong raw reports cho phép đối chiếu chính xác source đã chạy. Code không gọi network/LLM và không có learned weights. Dùng defaults đã ghi trong rules-baseline.md. Không sửa vocabulary sau smoke để tăng score.

## Kết quả đo trên fixture, không suy rộng

| Diagnostic | Measured value |
|---|---:|
| Exact character-span TP / FP / FN | 6 / 3 / 7 |
| Character-span precision / recall / F1 | 66,67% / 46,15% / 54,55% |
| End-to-end correction top-1 / top-3 | 6/13 / 6/13 |
| Oracle gold-span candidate recall@3 | 10/13 |
| Clean sentences có false finding | 1/10 |
| Valid entity spans bị sửa | 1/18 |
| Genuine entity typos được phát hiện | 0/2 |

Các tỷ lệ có support quá nhỏ để suy ra chất lượng thực. Preservation đứng một mình sẽ giấu việc bỏ sót cả hai entity typos. Không có confidence intervals hoặc unseen-identity evaluation.

## CPU diagnostic

Fresh Python 3.12.14 CLI process, Linux x86-64, AMD EPYC 9V74 80-Core Processor; một Python thread, batch 1. Warmup 100 calls, 1.000 timed calls, luân phiên 22 fixture sentences dài 12–45 raw code points.

| Measurement | Value |
|---|---:|
| Warm p50 / p95 | 1,616 / 4,764 ms |
| Serial throughput | 550,7 sentences/s |
| Whole-process peak RSS | 12.845.056 bytes |
| Seed JSON artifact | 1.745 bytes |
| Inference Python modules | 19.990 bytes |
| Combined inference bundle | 21.735 bytes |

Bundle không gồm Python interpreter/stdlib/evaluator. Peak RSS có cả CLI/data loading, không phải model-only RAM. Không đo cold process startup, pin CPU hoặc kiểm soát clock. Các số này thuộc seed vocabulary rất nhỏ; search đang quét toàn vocabulary, không ngoại suy latency/dung lượng cho complete lexicon.

## Error analysis

- Nguyễn Phú **Trọng** bị đề xuất thành Nguyễn Phú **Trong**: Vietnamese name chưa có trong seed; character evidence không đủ bảo vệ tên có dấu.
- “tiếng **Việt**” bị đổi thành “tiếng **Viết**”: closed-world lexicon thiếu từ hợp lệ tạo false positives. Không được coi OOV là chắc chắn sai.
- “quyễn” có candidates “quyển/quyền” cùng cost: baseline abstain. Cần context để rank đúng, không chỉ tăng threshold.
- “bóng truyền” không bị báo: các syllables đều trong lexicon; real-word confusion cần context. Bounded edit candidates cũng không đảm bảo có đáp án.
- “Pyhton” có candidate Python nhưng possible-name heuristic abstain: protection đổi false positives lấy missed true errors.
- Telex/VNI và “đag” chưa được giải quyết chắc chắn: thiếu decoder/error model và candidate margin còn yếu.

9 error-bearing records có source, reference và suggested text trong evaluation.json. Không đủ 30 failure records; không sinh thêm để làm đẹp report.

## Kết luận được phép rút ra

Inference/evaluation plumbing chạy được; evaluator phân biệt detection đúng với correction sai, và ghi cả false edits trên clean input. Baseline có những failure modes cụ thể cần kiểm chứng trên nguồn độc lập. **Chưa thể loại A/B/C hoặc kết luận model dưới 100 KB hữu ích chỉ từ fixture.**

Next experiment: xác minh và import authentic development source, dựng lexicon rộng có provenance, audit labels/duplicates; sau đó train hashed linear baseline và so với R tại matched false-positive rate. Không cần neural model hoặc LLM generation trước khi data gate đạt.

## Raw reports và replay

- [Evaluation + error records](results/R000-smoke/evaluation.json)
- [CPU + environment + source hashes](results/R000-smoke/cpu.json)
- Replay commands ở [rules baseline guide](../docs/rules-baseline.md); code hashes phải trùng nếu muốn đối chiếu chính xác measured implementation. CPU timings có thể thay đổi giữa lần chạy.
