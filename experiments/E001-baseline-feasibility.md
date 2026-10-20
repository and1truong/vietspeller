# E001 — Học xem machine learning thêm được gì so với rules

## Trạng thái và mục tiêu

Đây là bài học thí nghiệm sắp thực hiện, chưa có kết quả E001. R baseline/evaluator đã chạy được; [R000](R000-smoke-report.md) là diagnostic riêng. Chưa có learned L/LC/LCN models, training CLI hoặc threshold search.

Mục tiêu không phải đạt một production score. Người học cần hiểu cách đặt giả thuyết, fit một model đơn giản, giữ dữ liệu riêng và giải thích điều gì thay đổi khi thêm features. Model kém rules vẫn là kết quả học hợp lệ.

Đọc trước [training từ đầu](../docs/training-from-zero.md) và [benchmark](../docs/benchmark.md). Tra thuật ngữ ở [glossary](../docs/glossary.md).

## 1. Câu hỏi nhỏ đầu tiên

Rules có thể nhận “họcc” nhưng bỏ sót “bóng truyền” hoặc làm sai tên. Một classifier học từ examples có giúp một nhóm lỗi cụ thể hơn không? Đừng hỏi ngay “kiến trúc nào tốt nhất tiếng Việt”; câu hỏi đó quá rộng cho bài đầu.

Trước implementation, người học ghi: dự đoán ML sẽ giúp loại lỗi nào, dựa vào feature nào và case nào có thể làm dự đoán sai. Mentor review prediction, không yêu cầu phải đoán đúng.

## 2. Các phần bài tập, làm lần lượt

### Phần A — hiểu dữ liệu và điểm số

Chọn bài tập nhỏ tự viết với labels rõ, gồm token đúng, typo, tên/foreign terms và vài câu mơ hồ để thảo luận. Ghi rõ toy exercise. Có thể bắt đầu bằng vài chục examples; không dùng chúng để tuyên bố chất lượng tiếng Việt.

Giữ mọi variants cùng source group. Tách phần để fit và phần để kiểm tra; khi cần chọn cấu hình/threshold, thêm validation role rõ ràng. Demo fixtures hiện có vẫn là demo, không đổi tên thành independent test.

Bài tập: viết một record, chạy validator, tự tính TP/FP/FN cho vài predictions. Giải thích vì sao classifier báo mọi thứ là sai có thể có recall cao.

### Phần B — model nhỏ đầu tiên

Thiết kế local features trước khi xem hướng mentor ưu tiên. Có thể bắt đầu với ít explicit features để hiểu từng weight; rồi thử char n-gram Logistic Regression. Implementation/training sẽ được hướng dẫn ở bước code tiếp, không có command train sẵn trong tài liệu này.

Fit trên train, dùng validation khi chọn cấu hình, đọc predictions ở phần giữ riêng. Lưu features, weights, bias và labels/class order. Không chỉ lưu một score.

Bài tập: đưa một token qua feature vector và tính lại raw score bằng tay hoặc một hàm nhỏ. Chỉ ra phần nào do optimizer học, phần nào do người lập trình chọn.

### Phần C — một comparison và một ablation

So learned local classifier với R trên cùng examples/chính sách chấm. Nếu thêm context, giữ các phần còn lại và ghi thay đổi capacity/features. Ablation là bỏ một phần để xem nó thực sự đóng góp gì.

Một linear classifier trên token chưa tự có exact character-span output. Nếu candidate/minimal-edit code được dùng để tạo spans, phải ghi rõ chỗ đó để so cả classifier-level và end-to-end behavior một cách trung thực.

Bài tập: chọn 3 false positives và 3 false negatives nếu có đủ; tự phân loại lỗi do dữ liệu, features, candidates, ranking hay policy. Không sinh thêm failures để đạt quota báo cáo.

## 3. Các variants để nghiên cứu dần

| ID | Ý nghĩa bài học | Trạng thái |
|---|---|---|
| R | Dictionary/rules hiện tại, gồm protection/abstention cố định | Có implementation |
| L | Học local character evidence bằng linear classifier | Chưa triển khai |
| LC | Thêm bounded context features | Chưa triển khai |
| LCN | Nghiên cứu learned name/foreignness signals bên cạnh fixed protection | Chưa triển khai |
| LCN-Q | Thử quantized weights để học size/quality trade-off | Chưa triển khai |

R hiện đã có protected terms/name heuristics; không giả vờ nó là baseline hoàn toàn không có name handling. Khi làm name ablation, phân biệt fixed rules với learned features, và xem cả name preservation lẫn true-typo recall.

Không cần chạy hết bảng trong bài đầu. Chỉ mở variant mới khi có câu hỏi mà kết quả trước chưa trả lời được.

## 4. Hypotheses gợi ý để người học thử phản biện

- Local character features có thể giúp non-word errors nhưng chưa đủ cho nhiều real-word confusions.
- Context có thể phân biệt candidates hợp lệ về mặt chữ nhưng khác nghĩa.
- Name protection có thể giảm FP và đồng thời làm mất recall của typo thật trong tên.
- INT8 có thể giảm weights nhưng làm đổi scores/threshold decisions.

Đây là giả thuyết, chưa là findings. Viết một counterexample cho ít nhất một hypothesis và nói experiment nào rẻ nhất để phân biệt.

## 5. Đánh giá ở mức học tập

Trước tiên dùng cách chấm nhỏ mà người học tự kiểm tra được. Report raw counts, support, detection/correction riêng, ví dụ sai và dữ liệu đã dùng. Sau khi hiểu cơ chế, mới tăng tới nhiều slices, authentic independent evaluation và uncertainty estimates.

Matched false-positive rate nghĩa so recall khi hai cấu hình được chọn threshold để gây mức báo nhầm tương đương trên validation. Nó trả lời câu hỏi khác với so default thresholds. Current R chưa có learned/calibrated score; các heuristic cutoffs của nó cũng cần được ghi rõ.

Precision 98%, clean flag rate 1%, preservation 99,5%, bundle dưới 100.000 bytes và allowed quantization loss 1 percentage point từng là mục tiêu nghiên cứu đề xuất. Chúng không phải acceptance criteria sản phẩm hay điều kiện hoàn thành bài học. Nếu dùng chúng ở bài nâng cao, chốt cách đo trước khi nhìn kết quả và cho phép kết luận inconclusive.

## 6. Khi nào mới mở rộng dữ liệu?

Khi người học đã hiểu fit/predict và thấy giới hạn của toy data, thêm nguồn có quyền sử dụng, kiểm tra labels và source duplicates. Budgets 10–50K clean sources/tối đa 200K synthetic instances là gợi ý nghiên cứu lớn hơn, không minimum requirements để bắt đầu.

Lưu source/prompt/generator versions khi tạo dữ liệu. Đừng lấy vocabulary, threshold hoặc confusion weights từ test. Score trên synthetic-only data chưa chứng minh xử lý lỗi thật.

## 7. Kết quả học cần đạt

- Giải thích được vì sao một example có label đó và feature vector được tạo thế nào.
- Phân biệt fit parameters với chọn hyperparameters/threshold.
- Đọc được số đúng/sai, không chỉ báo F1.
- Nêu được ít nhất một điều learned model thêm được hoặc chưa thêm được so với R.
- Lưu được parameters/config để inference lại; chuẩn bị cho bài [TypeScript/Go](../docs/cross-language-inference.md).
- Viết một [report](report-template.md) gồm observation, interpretation và điều chưa biết.

Dừng để review sau mỗi phần nhỏ. Không tự train tất cả model families chỉ để săn score hoặc trông giống production project.
