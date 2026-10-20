# Bài thực hành: hiểu rules baseline đang chạy

## Học được gì và chưa có gì?

Baseline là mốc đơn giản để so phương pháp sau này. R baseline trong repo dùng dictionary và các rules do người lập trình chọn. Nó không thực hiện training và không có learned weights. Đây là bước quan sát input/output trước khi học fit model.

Đọc [learning guide](learning-guide.md) trước nếu các từ inference, candidate, span còn mới. Bài này giới thiệu code đang có, không yêu cầu chuẩn bị production dictionary.

## 1. Chạy một ví dụ

Từ repo root trên Bash: PYTHONPATH=src python -m vietspeller.cli check --artifact data/examples/bootstrap-lexicon.json --text 'Tôi đang họcc bài trên Kubernetes.'

Artifact là file vocabulary/configuration. Check đọc câu và trả JSON. Với ví dụ này, quan sát finding ở chữ c thừa: start 12, end 13, source text “c” và candidate replacement rỗng, tức xóa chữ đó. Input không tự bị sửa.

Findings là những lỗi được đề xuất. Abstentions là trường hợp giữ nguyên vì thiếu bằng chứng. Score là edit heuristic, chưa phải calibrated confidence. Demo_only nhắc seed vocabulary là đồ dùng bài học.

Thử tiếp “Tôi chơi bóng truyền.” và “Tôi gặp Nguyen.” Trước khi chạy, dự đoán output rồi giải thích nếu kết quả khác dự đoán. Không chỉ xem score; đọc cả phần không được báo.

## 2. Theo source code ở đâu?

| File | Vai trò |
|---|---|
| src/vietspeller/cli.py | Đọc command arguments và gọi chức năng tương ứng |
| src/vietspeller/text.py | Token units, normalization helpers và minimal edit spans |
| src/vietspeller/baseline.py | Load dictionary, candidate search, heuristic decision |
| src/vietspeller/evaluation.py | So output với gold labels |
| src/vietspeller/benchmark.py | Đo thời gian lặp lại và process memory |
| src/vietspeller/data.py | Kiểm tra record structure và một số split leakage |

API Python chính là RuleBaseline.load(path).check(text, profile). Path phải trỏ tới file artifact. Apply_suggestions là hàm riêng để áp dụng top candidates khi được gọi rõ; check không tự rewrite câu.

## 3. Các bước baseline làm

1. Tách tokens thành letter+combining units, giữ raw offsets; chưa phải word segmentation tiếng Việt đầy đủ.
2. Giữ các exact lexicon entries và protected phrases/terms đã khai báo; so bằng case/NFC key.
3. Bảo vệ một số URLs, email, inline code và snake_case patterns; đây không phải parser cho mọi loại code.
4. Tính partial orthographic evidence. Các phonology issues chủ yếu là diagnostics; chưa có full syllable automaton hoặc learned feature use.
5. Quét candidate vocabulary, gồm syllables và một số single-token protected terms, tính edit cost.
6. Dùng hand-chosen rules để đề xuất hoặc abstain, rồi tính minimal raw-text edit.

Protected terms không phải NER. Thuật ngữ/tên chưa được khai báo có thể bị xử lý sai. Không truyền gold entities từ evaluation vào detector để làm kết quả dễ hơn.

## 4. Candidate distance có nghĩa gì?

Edit cost mô tả độ gần chữ, không phải xác suất. Insert/delete có cost 1; generic substitution 1; diacritic-related substitution 0,25; adjacent transposition 0,75. Đây là lựa chọn do người viết đặt để bắt đầu thí nghiệm, chưa được học từ tần suất lỗi người thật.

Candidate search giữ tối đa ba words với cost không quá 1,25. Decision có thêm cutoffs: best cost trên 1 hoặc hai candidates gần nhau dưới margin 0,35 có thể khiến abstain. Model có thể biết đáp án trong candidates mà vẫn giữ nguyên vì ambiguous.

Ví dụ “quyễn” gần cả “quyển” và “quyền”. Không có context/frequency ranking nên không biết chắc câu đang nói tới một quyển sách. Nếu “truyền” đã trong lexicon, exact membership giữ nguyên và real-word confusion có thể bị bỏ sót hoàn toàn.

Score hiển thị dùng 1 chia 1 + cost. Không đọc score 0,8 thành 80% đúng. [Training guide](training-from-zero.md) giải thích score của learned Logistic Regression khác nó thế nào.

## 5. Vì sao abstain và vì sao vẫn có lỗi?

Rules hiện abstain với foreign/identifier, possible ASCII capitalized name, informal ASCII, no bounded candidate, weak candidate hoặc ambiguous candidates. Một tên có dấu giống tiếng Việt vẫn có thể bị báo nhầm; một typo viết hoa có thể bị bỏ sót vì giống tên. R000 cho thấy cả hai.

Mục đích học là nhìn thấy trade-off này. Không thêm từng đáp án test vào allowlist rồi coi model đã hiểu tên. Với personal dictionaries thật, entry do người dùng xác nhận là một điều kiện sử dụng khác; được theo dõi ở issue #2.

## 6. Unicode và candidate spans

Minimal edit bỏ prefix/suffix không đổi để trả vùng nhỏ cần thay. So theo cụm Vietnamese base+combining giúp không tách dấu khỏi chữ nền. Source offsets vẫn trên input gốc; canonical-equivalent text không cần edit.

Một candidate khác boundaries không được nhét vào cùng replacement span của candidate đầu. Candidate list trong một finding chỉ giữ các phương án tương thích source span. Current code chưa có full UAX #29 segmentation hoặc general normalization mapping; đó là bài nâng cao riêng.

Input tối đa 256 raw code points; candidate search chỉ xét token không quá 32 NFC code points. Code báo lỗi thay vì silently truncate input dài. Search quét vocabulary với chi phí khoảng V nhân L bình phương, nên timing của seed vocabulary không đại diện full lexicon.

## 7. Artifact đang chứa gì?

Bootstrap JSON có schema_version 1, demo_only true, provenance, syllables và protected_terms. Các names cho biết loại dữ liệu, không làm nó thành learned model. Provenance mô tả nguồn; validator không chứng minh lexical validity hoặc quyền dùng.

Syllables là Vietnamese-letter units; protected terms có thể nhiều tokens, yêu cầu whitespace giữa các tokens khi khớp phrase. Case/NFC matching không thay raw text. Vocabulary hiện do dự án viết, rất nhỏ và chưa chọn project license.

## 8. Chấm và đo để học

Chạy: PYTHONPATH=src python -m vietspeller.cli evaluate data/examples/illustrative.jsonl --artifact data/examples/bootstrap-lexicon.json --split demo --allow-demo --output runs/evaluation.json

Evaluate so predictions với gold. Allow-demo là nhắc nhở không diễn giải đây là independent score. Runs/ là nơi output tạm được gitignore. Đọc meanings/mẫu số ở [benchmark](benchmark.md), rồi xem [R000 report](../experiments/R000-smoke-report.md).

Chạy CPU diagnostic: PYTHONPATH=src python -m vietspeller.cli benchmark data/examples/illustrative.jsonl --artifact data/examples/bootstrap-lexicon.json --split demo --allow-demo --warmup 100 --repeat 1000 --output runs/cpu.json

Kết quả đo warm check(), gồm tokenization, candidates và offsets. Peak RSS là whole CLI process. Chưa có cold startup, runtime-only RAM hoặc length-bucket comparisons. Ta đo để hiểu chứ chưa cần đạt SLA.

External files có thể được evaluate bằng artifact khác và split validation/test. Chỉ khai demo_only false khi thật sự hiểu source và mục đích; đổi flag không làm dữ liệu tự nhiên hoặc độc lập hơn. Tool vẫn ghi unverified_external_evaluation.

## 9. Evaluator biết gì và chưa biết gì?

Exact spans, typed labels, token units, correction top-K, clean-text errors và entity diagnostics đã có. Gold spans chỉ được dùng cho oracle candidate measurement riêng; không đưa cho detector. Các edits qua nhiều tokens/gaps ngoài token có thể không có bounded candidate, và bị tính miss.

Gold variants cùng token được collapse ở token metric. Sentence exact dùng first replacement và NFC equivalence; chưa có mọi alternate sentence reference. Unseen identity split, confidence intervals và oracle ranker accuracy chưa được triển khai.

Abstentions không nên bị UI trình bày như confirmed error highlights mà vẫn loại khỏi metrics. Đây là ví dụ tại sao một measurement phải khớp hành vi ứng dụng, dù hiện ta chỉ học CLI.

## Bài tập

1. Chỉ ra constants/rules do người viết đặt trong baseline.py; có bước optimizer nào không?
2. Thử một câu đúng chứa từ chưa có trong seed. Quan sát FP hoặc abstention.
3. Tìm một typo có candidate nhưng không thành finding, rồi đọc reason.
4. Giải thích vì sao một baseline đúng trên 22 fixtures chưa đủ kết luận ngoài đời.
5. Chọn một failure case mà chỉ thêm dictionary không giải quyết được. Thử thiết kế feature cho bài học tiếp theo.

Không cần tự hoàn thiện engine trong bài này. Điểm hoàn thành là theo được một example qua code và phân biệt observed behavior với hypothesis.
