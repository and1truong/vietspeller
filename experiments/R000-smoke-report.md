# R000 — đọc kết quả của bài kiểm tra end-to-end đầu tiên

Trạng thái: đã chạy ngày 2026-10-20. Đây là diagnostic/smoke exercise, không phải E001 hoặc independent quality benchmark. “Smoke check” nghĩa thử các phần có chạy nối nhau được không, chưa chứng nhận chất lượng tổng quát.

## 1. Câu hỏi bài học

Rules baseline đọc text, tạo candidates, tính raw offsets và được evaluator chấm ra sao? Ta có thể nhìn thấy các failure modes nào ngay với ví dụ nhỏ?

Không có training trong run này. Không có weights được fit hoặc optimizer. Không chọn threshold/model dựa trên scores này. Đây là điểm xuất phát để học sự khác nhau giữa code hoạt động và model học tốt.

## 2. Dữ liệu đã dùng

22 project-authored records chứa 13 gold edits, 10 clean sentences, 18 valid entity spans và 2 lỗi thật đã gắn nhãn trong entity surfaces. Seed vocabulary có 138 syllables và 18 protected terms/phrases.

Vocabulary và examples phục vụ cùng diagnostic, không phải độc lập. Chưa có authentic source benchmark, train/validation/test experiment hoặc annotation agreement audit. Code/data/artifact SHA-256 trong raw reports chỉ giúp nhận diện chính xác inputs/source đã chạy; hash không chứng minh labels đúng.

Đây là measured output có thật, không phải số liệu minh họa. Nhưng phạm vi kết luận chỉ là run này.

## 3. Đếm đúng/sai trước khi đọc tỷ lệ

| Measurement | Giá trị đã đo | Cách đọc |
|---|---:|---|
| Exact-span TP / FP / FN | 6 / 3 / 7 | 6 gold spans được tìm đúng, 3 báo nhầm, 7 bỏ sót |
| Precision | 66,67% | 6 trong 9 predicted spans đúng |
| Recall | 46,15% | 6 trong 13 gold spans được tìm |
| F1 | 54,55% | Kết hợp precision và recall theo công thức của metric |
| Correction top-1 / top-3 end-to-end | 6/13 / 6/13 | Đáp án trong candidates không cứu được lỗi detector bỏ sót |
| Oracle candidate recall@3 | 10/13 | Khi cho sẵn vị trí gold, generator có đáp án cho 10 lỗi |
| Clean sentences bị báo nhầm | 1/10 | Không chỉ đo trên câu lỗi |
| Valid entity spans bị sửa | 1/18 | Bảo vệ tên chưa hoàn hảo |
| Entity typos được phát hiện | 0/2 | Bỏ sót cả hai lỗi tên đã gắn nhãn |

Đọc [benchmark lesson](../docs/benchmark.md) để tự tính các tỷ lệ. Mẫu số quá nhỏ để kết luận về toàn tiếng Việt; report chưa có confidence intervals. Không đổi việc “18 tên thì giữ 17” thành một lời hứa cho names chưa từng gặp.

## 4. Xem examples làm sai

- “Nguyễn Phú Trọng” bị đề xuất thành “Nguyễn Phú Trong”: tên có dấu giống một từ khác trong seed. Dictionary và character proximity không tự hiểu đây là tên.
- “tiếng Việt” bị đề xuất thành “tiếng Viết”: một từ đúng thiếu trong seed tạo false positive. OOV chưa chắc sai.
- “quyễn” không được sửa vì “quyển/quyền” có cost gần nhau: abstain giữ nguyên, cho thấy nhu cầu context thay vì ép chọn.
- “bóng truyền” không bị báo vì các syllables có trong lexicon: đây là real-word confusion mà membership không giải quyết.
- “Pyhton” có candidate Python nhưng possible-name heuristic abstain: bảo vệ từ giống tên có thể che genuine typo.
- Telex/VNI và “đag” chưa được giải quyết chắc chắn: chưa có full decoder/error model và candidate margin còn hạn chế.

Raw evaluation có 9 error-bearing records với source/reference/suggested text. Không cần sinh thêm lỗi để đạt một quota report. Với bài học này, giải thích được một vài errors quan trọng có giá trị hơn giấu failures sau một score chung.

## 5. CPU diagnostic: học cách đọc các khoản chi phí

Môi trường đã đo: Python 3.12.14, Linux x86-64, AMD EPYC 9V74 80-Core Processor, một Python thread, batch 1. Warmup 100 calls, đo 1.000 calls luân phiên 22 câu dài 12–45 raw code points.

| Measurement | Giá trị đã đo | Ý nghĩa |
|---|---:|---|
| Warm p50 / p95 | 1,616 / 4,764 ms | Phân vị thời gian qua các calls đã warmup |
| Serial throughput | 550,7 sentences/s | Tính từ tổng thời gian các timed calls |
| Whole-process peak RSS | 12.845.056 bytes | Có interpreter, CLI và data loading, không chỉ dictionary |
| Seed JSON artifact | 1.745 bytes | File dữ liệu nhỏ, không phải learned weights |
| Inference Python modules | 19.990 bytes | Source modules cần cho baseline inference |
| Combined inference bundle | 21.735 bytes | Artifact + modules, chưa gồm interpreter/stdlib/evaluator |

Không có measured cold process startup hoặc runtime-only RAM; không pin CPU/clock. Không dùng timing vocabulary 138 syllables để dự đoán full vocabulary. Các con số được giữ nguyên từ run gốc; việc viết lại tài liệu không phải một run đo mới.

## 6. Kết luận hợp lệ

Các phần inference/evaluator/CPU measurement chạy nối nhau được. Evaluator có thể ghi cả missed errors và false edits trên clean input. Những examples cụ thể chỉ ra giới hạn của vocabulary, context và name heuristics.

Chưa được kết luận A/B/C nào tốt nhất, model dưới 100 KB đủ dùng hoặc hệ thống sẵn sàng production. Cũng chưa được nói đã hoàn thành training lifecycle: run này không train gì.

## 7. Bài tập đọc report

1. Tính lại precision và recall từ TP/FP/FN.
2. Vì sao oracle coverage 10/13 cao hơn end-to-end correction 6/13?
3. Nếu không sửa gì, preservation có thể cao nhưng những số nào sẽ kém?
4. Vì sao thêm “Trọng” hoặc “Việt” sau khi thấy errors là run với điều kiện mới, chưa chứng minh biết xử lý tên lạ?
5. Chọn một failure case cần thêm context, và một case có thể bắt đầu bằng dictionary tốt hơn.

Bước học tiếp theo là hiểu [training linear model](../docs/training-from-zero.md) bằng bài nhỏ, rồi thiết kế [E001](E001-baseline-feasibility.md). Khi muốn kết luận rộng hơn, bổ sung dữ liệu độc lập có provenance; không cần đợi tới đó mới học fit/predict.

## Raw reports và replay

- [Evaluation và errors](results/R000-smoke/evaluation.json).
- [CPU/environment/source hashes](results/R000-smoke/cpu.json).
- [Commands và source walkthrough](../docs/rules-baseline.md).

Code hashes phải khớp nếu muốn đối chiếu đúng implementation đã đo. Timings có thể khác giữa lần chạy. Không sửa raw snapshots chỉ để làm tài liệu trông đẹp hơn.
