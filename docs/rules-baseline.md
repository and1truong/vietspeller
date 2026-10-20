# R baseline — executable diagnostic, not a production model

## API và CLI

`RuleBaseline.load(path).check(text, profile)` trả findings và abstentions, giữ nguyên input. Findings dùng raw Unicode code-point spans và tối đa ba minimal replacements có chung source span. Một candidate khác boundary không được gán vào span của candidate đầu tiên. `apply_suggestions` là hàm opt-in cho top candidate; CLI check không auto-correct.

```sh
PYTHONPATH=src python -m vietspeller.cli check --artifact data/examples/bootstrap-lexicon.json --text 'Tôi đang họcc bài trên Kubernetes.'
PYTHONPATH=src python -m vietspeller.cli evaluate data/examples/illustrative.jsonl --artifact data/examples/bootstrap-lexicon.json --split demo --allow-demo --output runs/evaluation.json
PYTHONPATH=src python -m vietspeller.cli benchmark data/examples/illustrative.jsonl --artifact data/examples/bootstrap-lexicon.json --split demo --allow-demo --warmup 100 --repeat 1000 --output runs/cpu.json
```

Để chấm external test, truyền artifact riêng và chọn `--split test` (default). Files tất cả splits có thể truyền cùng invocation để validation bắt cross-file leakage trước khi chọn partition. Chỉ bỏ demo flag trong artifact khi nguồn và data gate đã được xác minh; CLI không thể tự chứng minh provenance. External evaluation vẫn được đánh dấu unverified, không tự biến thành certified benchmark.

## Artifact v1

JSON gồm `schema_version: 1`, `demo_only` boolean, `provenance` nonempty string, `syllables` list và `protected_terms` list. Syllables phải là một Vietnamese-letter unit; chúng không được coi là lexically valid chỉ vì qua validator. Protected terms có thể gồm nhiều tokens, phải khớp phrase với whitespace giữa tokens. Case/NFC matching giữ nguyên source text.

Bundled vocabulary do dự án viết, rất nhỏ, chưa có license được chọn; không phải toàn bộ âm tiết tiếng Việt. Không build dictionary hoặc protected terms từ evaluation gold. Known terms là explicit vocabulary protection, **không phải NER**, và có thể làm benchmark dễ giả tạo nếu terms lấy từ test. Diagnostic fixture và seed vocabulary được thiết kế cùng nhau, nên không có independence claim.

## Algorithm và abstention

1. Tokenize letter+combining sequences, giữ raw offsets. Exact lexicon/term match được giữ.
2. Bảo vệ URLs, email, inline code và snake_case identifiers theo pattern hẹp. Không phải code parser đầy đủ.
3. Orthography cung cấp foreign-character và partial necessary-constraint evidence. Chưa có full syllable automaton; các phonology issues hiện là diagnostics, chưa được học hoặc calibrate như features.
4. Sinh candidates bằng weighted optimal-string-alignment edit distance: insert/delete 1, generic substitute 1, diacritic-related substitute 0,25, adjacent transposition 0,75. Cắt candidate distance ở 1,25, giữ tối đa ba; đây là hand-chosen hypotheses, không empirical error probabilities.
5. Abstain khi foreign/identifier, possible ASCII capitalized name, informal ASCII, không có candidate, top candidates cách nhau <0,35 hoặc best cost >1. Unknown non-ASCII name giống Vietnamese vẫn có thể bị báo nhầm; unknown lowercase ASCII có thể bị sửa nhầm. Bắt buộc đánh giá hai nhóm này trên real data.
6. Một contiguous minimal edit được tính theo Vietnamese base+combining clusters, tránh cắt tone mark. Đây chưa là complete UAX #29 implementation. Label diacritic hiện heuristic, chưa phân loại chắc chắn misplaced mark hoặc keyboard cause.

`score = 1/(1+cost)` được ghi rõ uncalibrated heuristic. Không diễn giải 0,8 thành 80% đúng. Rule signal hiện chủ yếu là vocabulary/protection và candidate filtering; chưa có context model, frequency ranking hoặc full Telex/VNI decoder.

Input limit 256 raw code points, token candidate search limit 32 NFC code points. Dài hơn không bị silently truncate. Search quét vocabulary, O(V × L²), cần indexing hoặc pruning khi vocabulary lớn. Không lấy timing với seed lexicon làm timing cho vocabulary thật.

## Evaluator semantics

Không đưa gold entities hoặc gold spans vào detector. Oracle candidate recall là phép đo riêng: dùng gold location để hỏi generator có tạo đáp án đúng trong ba candidates không. Các zero-length gaps ở token boundaries và edits qua nhiều tokens hiện có thể không có candidate; được tính miss, không bỏ mẫu số. Oracle ranker accuracy chưa được đo.

Character-span metric match chính xác one-to-one. Token-span dùng letter units của baseline, không gọi chúng là lexical words. Các gold edits cùng token được collapse thành token-span set. Missing-character gap trong token quy về token đó; gap ngoài token giữ raw anchor.

End-to-end correction top-1/top-3 dùng toàn bộ gold edits làm mẫu số, bao gồm missed detections. Edit precision còn tính cả edits sai trên clean text. Sentence exact dùng first-replacement reference và NFC equivalence; chưa có đầy đủ acceptable sentence alternatives.

Valid-entity preservation đo trên suggested top edits, cạnh recall trên genuine entity typos. Abstentions không được render như error highlights; nếu UI gạch chân thì phải đưa chúng vào finding metrics. Metrics chưa có CIs, entity-identity-disjoint verification hoặc authentic error distribution. Không có assertions ép smoke scores phải cao.

CPU command đo warm end-to-end check(), gồm tokenization, candidate search và offsets. Peak RSS là whole CLI process high-water mark; cold startup và baseline-runtime-only RAM chưa đo. Bundle bytes gồm artifact và các Python inference modules, không gồm interpreter/stdlib/evaluator. Báo source hashes và raw-byte data/artifact hashes để replay.
