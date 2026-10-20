# Đánh giá model: đọc được điểm số và biết điểm số chưa nói gì

## Mục tiêu bài học

Tự tính precision/recall từ vài examples, phân biệt detection với correction và đọc được report của repo. Benchmark là tập dữ liệu cùng cách chấm nhất quán để so sánh; không cần một hệ thống benchmark lớn mới được học metrics.

Evaluator hiện đã có exact character/token/typed-span metrics, correction, oracle candidate coverage và entity diagnostics. Chưa có independent benchmark dataset, confidence intervals hoặc xác minh unseen identities. [R000](../experiments/R000-smoke-report.md) chỉ là diagnostic trên fixtures.

## 1. TP, FP và FN bằng một phép đếm

Ví dụ giả định để tính, không phải kết quả R000: trong dữ liệu có 10 lỗi thật. Hệ thống báo 8 findings; 6 findings khớp lỗi thật và 2 findings báo nhầm. Ta có TP = 6, FP = 2, FN = 4.

Precision = TP chia TP + FP = 6/8 = 75%. Nó trả lời: trong những lỗi hệ thống báo ra, bao nhiêu là lỗi thật?

Recall = TP chia TP + FN = 6/10 = 60%. Nó trả lời: trong những lỗi thật, bao nhiêu đã được tìm thấy?

F1 = 2 nhân precision nhân recall, chia precision + recall; ví dụ này khoảng 66,67%. F1 cân bằng hai tỷ lệ theo một cách, nhưng chưa thể hiện mọi chi phí. Trong editor, báo nhầm tên người liên tục có thể gây khó chịu hơn bỏ sót một typo; cần hiểu context sử dụng thay vì chỉ chọn score cao nhất.

Không có gold errors hoặc predictions thì một số mẫu số bằng 0. Evaluator trả null khi tỷ lệ không xác định, không tự biến thành 100%.

## 2. “Tìm đúng lỗi” được định nghĩa ra sao?

Gold là đáp án được gắn nhãn. Exact character-span match yêu cầu start và end trùng gold, one-to-one. Nếu gold chỉ một chữ c nhưng detector highlight cả token, đó không phải exact character-span TP, dù có thể tìm đúng token.

Token-span metric xem vùng lỗi theo token units. Tokenizer hiện dùng letter units, chưa phải Vietnamese lexical words. Nhiều edits trên cùng một token có thể được collapse ở metric này. Vì vậy đọc cả character và token metrics để thấy lỗi boundary.

Typed-span metric còn yêu cầu label loại lỗi đúng. Vị trí đúng nhưng gọi missing_diacritic thành wrong_diacritic có thể được tính đúng ở untyped metric và sai ở typed metric. Không gộp hai câu hỏi này.

Gap edit cho ký tự bị thiếu cần khớp anchor chính xác. Ký tự lặp có thể tạo nhiều scripts hợp lý; guideline và acceptable references cần rõ, không tự mặc định evaluator đã giải quyết mọi ambiguity.

## 3. Detection đúng chưa đồng nghĩa correction đúng

Với một span đã tìm đúng, candidate đầu có thể sai. Ví dụ “quyễn” có candidates “quyển/quyền”; context quyết định lựa chọn nào phù hợp.

- Candidate recall@K: đáp án có trong K candidates đầu không?
- Oracle-span: cho sẵn vị trí gold để xem riêng generator/ranker. Đây là phép đo dễ hơn, không phải năng lực tìm lỗi tự động.
- End-to-end top-1/top-3: cả detector và candidates phải đưa tới correction hợp lệ; lỗi detector bỏ sót vẫn nằm trong mẫu số toàn gold edits.
- Edit precision: số edits sửa đúng trên tổng suggested edits, gồm cả sửa nhầm câu sạch.
- Sentence exact match: sau edits, cả câu khớp reference hay không? Đọc riêng clean và noisy sentences.

Evaluator hiện có oracle candidate recall@3, chưa có oracle ranker accuracy đầy đủ. Nó dùng first-replacement sentence reference cùng NFC equivalence; chưa hỗ trợ mọi câu sửa khác nhưng hợp lệ. Xem [baseline guide](rules-baseline.md) để hiểu semantics cụ thể.

## 4. Vì sao phải có câu đúng và tên riêng?

Model báo mọi thứ là lỗi có thể tìm đủ gold errors nhưng làm hỏng câu đúng. Clean-sentence flag rate đếm số câu sạch có bất kỳ finding chia tổng câu sạch. False findings trên 1.000 clean tokens đo ở một đơn vị khác; không gọi hai con số này là cùng một FPR.

Entity preservation hỏi tên đúng có bị sửa không. Nhưng hệ thống không sửa gì cũng có preservation 100%; phải đọc cạnh recall trên typo thật trong tên. “Pyhton” khi đã xác nhận định viết Python là một ví dụ cần được phát hiện, không phải chỉ bảo vệ mọi từ viết hoa.

Nếu UI gạch chân abstentions, người dùng vẫn nhìn thấy một finding. Cách chấm hiện không tính abstention vào findings; integration phải nhất quán với điều người dùng thực sự thấy.

## 5. Một con số chung có thể giấu điều gì?

Slice là một nhóm examples: lỗi dấu, real-word errors, tên lạ, Telex/VNI, thiếu dấu, nhiều lỗi, từ vùng miền, technical code-switching, NFC/NFD hoặc emoji trước lỗi. Report support, tức số examples/events của nhóm đó, cạnh score.

Một slice có một example làm đúng cho 100%, nhưng không chứng minh đã giải quyết nhóm lỗi. Current evaluator có domain/profile/source slices và gold error labels; nó chưa tự biết một identity là unseen so với train hay aliases của identity đó.

Nhóm tên unseen cần được giữ riêng theo tên/identity, không chỉ random split câu có cùng tên. Personal dictionary nếu được dùng phải ghi rõ điều kiện đánh giá; không thêm từ sau khi xem test rồi gọi đó là generalization.

## 6. Threshold, validation và test

Threshold là mức điểm để quyết định báo lỗi. Hạ threshold thường có thể tăng cả số lỗi tìm được và số báo nhầm; không tự làm weights học tốt hơn.

Chọn threshold/cấu hình trên validation. Giữ final test cho lựa chọn đã chốt. Nếu xem test errors rồi liên tục sửa theo chúng, tập đó đang đóng vai trò development. Đừng gọi lại nó là independent test mà không giải thích.

Rules baseline hiện dùng heuristic cutoffs cố định, chưa có training/calibrated threshold search. Mục tiêu 98% precision trong kế hoạch cũ là ví dụ nghiên cứu nâng cao; không phải điều kiện để bài học đầu được coi là thành công.

## 7. CPU và kích thước: đo để hiểu

Latency là thời gian một request. p50 là khoảng giữa các lần đo; p95 cho biết phần lớn lần đo nằm dưới mốc nào. Throughput là số câu trên một giây. Đừng lấy reciprocal của p95 rồi gọi đó là measured throughput.

Benchmark CLI mặc định warmup 100 calls, đo 1.000 calls, batch 1 trên một Python thread. Warmup giúp tách một số chi phí khởi động khỏi repeated calls; cold startup là một phép đo riêng, hiện chưa có.

Ghi CPU, OS, library/Python versions, input lengths và artifact/source hashes để hiểu cùng code có thể cho timing khác trên máy khác. Ở bài đầu chỉ cần replay và quan sát; CPU pinning/frequency control là phần nâng cao.

Model weights không bằng whole-process RAM. RSS gồm interpreter, loaded code, dữ liệu và bộ nhớ khác. Bundle size phải cho biết có gồm dictionary/tokenizer/runtime không. Current report tách artifact và Python inference modules, loại interpreter/stdlib/evaluator; runtime-only RAM và length buckets chưa được đo.

## 8. Khi nào cần bộ đánh giá lớn hơn?

Khi cần kết luận rộng hơn toy exercise, dùng nguồn độc lập, kiểm tra duplicates và có nhiều nhóm lỗi. Các con số 1.000 câu sạch, 500 câu lỗi và 300 challenge cases trong kế hoạch cũ là starting budgets nghiên cứu, không phải số lượng tối thiểu để học.

Dữ liệu curated có tỷ lệ lỗi được chọn bằng tay, không mặc định giống tỷ lệ lỗi khi người dùng gõ thật. Synthetic-only score có thể phản ánh generator nhiều hơn ngôn ngữ thực.

Confidence intervals là cách biểu diễn bất định; khi học phần này, resample theo source group để không coi 10 variants của cùng câu là 10 quan sát độc lập. Evaluator chưa triển khai CIs; không diễn giải report hiện tại như có chúng.

## Bài tập

1. Tự tính ví dụ 10 gold errors ở đầu bài, rồi tăng FP từ 2 lên 6 xem precision đổi thế nào.
2. Đọc [R000](../experiments/R000-smoke-report.md): vì sao 6 TP, 3 FP, 7 FN cho precision 6/9 và recall 6/13?
3. Tìm một prediction đúng vị trí nhưng correction sai; metric nào phải thay đổi?
4. Giải thích vì sao preservation cao mà typo recall bằng 0 chưa phải kết quả tốt.
5. Chỉ ra một kết luận report có thể hỗ trợ và một kết luận chưa thể hỗ trợ.

Điểm hoàn thành: đọc được mẫu số và semantics, không cần score cao. Dùng [report template](../experiments/report-template.md) để ghi điều quan sát và điều chưa biết.
