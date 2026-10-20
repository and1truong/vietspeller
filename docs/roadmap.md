# Roadmap và phase gates

Trạng thái: **Phase 1 contract drafted; Phase 2 tooling scaffolded.** Data gate chưa đạt. Chưa có authentic data, independent gold benchmark, hoặc trained baseline.

| Phase | Deliverable | Gate trước khi chuyển tiếp |
|---|---|---|
| 1. Definition | Taxonomy, offset/profile/output contract, unresolved policy | Giải thích và adjudicate 20 contrast cases; không còn bất đồng ảnh hưởng metric definition |
| 2. Dataset | Provenance manifests, annotation guideline, generator design, frozen source splits | 100% validation checks pass; licenses verified; double-annotation pilot ≥100 câu; independence/duplicate audit xong |
| 3. Baseline | Rules/dictionary + hashed linear baseline, E001 report | Report matched-FPR recall, all required slices và resource costs; không bắt buộc đạt quality target để được học sang phase tiếp theo |
| 4. Tiny ML | CRF/CNN/BiGRU/Transformer experiments khi có câu hỏi | Ít nhất một matched-budget comparison và meaningful ablation; select theo preregistered objective, hoặc kết luận chưa có model đủ tốt |
| 5. Correction | Candidate generation/ranking, calibrated keep-original | Candidate recall@K + oracle-span/end-to-end metrics; freeze suggestion threshold trên validation; đặt auto-edit precision target riêng trước auto-correct |
| 6. Names | Protection/joint/separate comparison | Entity-disjoint evaluation; báo preservation cạnh recall trên typo trong tên; chọn policy bằng measured trade-off |
| 7. Production | Inference API, artifact packaging, CPU report, limitations | Raw-offset/grapheme/IME integration checks pass; offline test pass; numeric latency/RAM limits được chọn và freeze theo CPU/app thực trước benchmark |

Phase 6 là reporting milestone; foreign-name requirements đã phải có từ Phase 1/E001. Không đợi tới cuối mới thêm tên riêng.

Gate là yêu cầu có bằng chứng hoặc giải quyết dependency. Baseline không đạt quality vẫn là kết quả hợp lệ để loại một cấu hình; không che giấu failure để “qua phase”. Production gate khác research gate.

## Learning loop

Trước mỗi experiment: người học ghi prediction và lý do; mentor review assumptions; người học implement/run; mentor review code/metrics; hai bên chọn experiment tiếp dựa trên error analysis. Không xin approval cho routine tooling. Khi người học yêu cầu full implementation thì cung cấp trực tiếp.

Việc tiếp theo: điền hypotheses của E001, adjudicate examples và chọn một nguồn authentic cho development. Scaffold không gọi LLM hoặc tải dataset tự động. Provider/credential setup sẽ làm khi bắt đầu LLM generation, không lưu API keys vào repo.
