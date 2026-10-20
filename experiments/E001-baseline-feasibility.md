# E001 — Precision-constrained baseline feasibility

Status: designed, not run. Không có model hoặc benchmark results.

## Quyết định cần hỗ trợ

Có nên giữ cấu hình dưới 100 KB làm ứng viên chính cho editor? Loại được một cấu hình không chứng minh mọi thuật toán cùng budget đều bất khả thi.

## Hypotheses — viết trước implementation

- H1: orthographic rules cung cấp non-word recall nhưng foreign names làm precision giảm nếu chỉ dùng dictionary membership.
- H2: context features cải thiện real-word recall ở matched clean-text flag rate.
- H3: name signals giảm false positives nhưng hard protection có thể che typo thật trong tên.
- H4: INT8 weights giữ được operating point trong tolerance đo được; đây chưa phải giả định được chấp nhận.

Người học điền bằng lời của mình: hypothesis nào có khả năng sai nhất, failure example cụ thể, false-positive/false-negative nào tốn kém hơn trong editor? Không đặt expected F1 tùy ý.

## Variants

| ID | Configuration | Câu hỏi |
|---|---|---|
| R | Dictionary + orthographic rules | Luật làm được bao nhiêu? |
| L | R + hashed char n-gram Logistic Regression | Learned local evidence thêm gì? |
| LC | L + bounded context features | Context có giá trị không? |
| LCN | LC + conservative name/foreign-term signals | Giảm false positives bằng gì, có che lỗi không? |
| LCN-Q | LCN với quantized weights | Artifact budget có đạt mà giữ operating point không? |

Train/validation giống nhau giữa variants. Ablations trên cùng feature/model budget; log khi thêm context làm thay đổi capacity hoặc feature collisions. Name-on/off tách khỏi context-on/off để tránh quy kết nhầm lợi ích.

## Preconditions

Data gate trong roadmap phải đạt. Tạo development set và giữ final independent test riêng. Fixture chỉ dùng contract checks. Dictionary/statistics phải có provenance; chỉ fit trên train hoặc external resource được khai báo, không rút vocabulary từ test.

Starting training budget: 10–50K clean source sentences, tối đa 200K initial synthetic instances; chạy subset learning curves trước khi tăng. Có clean negatives và authentic errors; chưa mặc định synthetic ratio tối ưu. Sample weighting chỉ được chọn trên validation.

## Operating point và go/no-go

Proposed validation targets: precision ≥98%, clean-sentence flag rate ≤1%, valid-entity preservation ≥99,5%. Chưa có product requirement khẳng định những mức này đủ dùng.

Chọn threshold trên validation; báo uncertainty và matched-FPR recall trên development evaluation partition độc lập. Không chọn threshold lại bằng test. Nếu không có threshold thỏa thì report infeasible, không đổi mẫu số hoặc bỏ slice khó.

LCN-Q cần toàn inference artifact <100.000 bytes; báo uncompressed size. So với FP32, preregister allowed recall loss ≤1 percentage point ở matched constraints; nếu khoảng tin cậy chưa phân biệt được, kết luận inconclusive và thu thêm dữ liệu.

Tiếp tục A nếu operating point hữu ích và resource budget đạt. Nếu real-word recall không đủ cho scope, thử B/C; chưa đặt recall gate số học trước khi biết prevalence và cost. Không loại B/C khi chưa train chúng. CPU timings chỉ báo measured values, chưa hứa latency số học.

## Deliverables và stop rule

Run manifest (git/data/artifact hashes, config, seed, environment), per-slice metrics/support, confidence intervals, PR curves, artifact accounting và ít nhất 30 error-analysis examples nếu có đủ lỗi. Phân tích FP/FN và names-with-typos.

Dừng vòng đầu sau R/L/LC/LCN và quantization check, rồi review. Không tự mở thêm model families chỉ để săn score. Candidate recall@3 trên gold spans có thể là follow-up tách riêng để quyết định correction pipeline.

## Bài tập implementation đầu tiên

Thiết kế lexicon interface và feature extractor trên giấy trước. Trả lời: âm tiết hợp cấu trúc nhưng không nằm trong từ điển có chắc sai không? Làm sao xử lý “Nguyen”, “deploy”, và một tên lạ viết thường? Sau đó triển khai R và đưa 10 false positives cùng 10 false negatives để review. Chưa cần neural network.
