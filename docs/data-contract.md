# Dataset contract v1

JSONL UTF-8, một record mỗi dòng. Record fields:

| Field | Quy ước |
|---|---|
| schema_version | Integer 1 |
| id | Unique trong toàn dataset version |
| group_id | Nhóm nguồn để split: toàn document/thread và mọi derived examples |
| split | demo, train, validation hoặc test |
| profile | strict hoặc informal |
| domain | general, technical, chat hoặc domain đã ghi trong manifest |
| text | Unicode gốc, không normalization khi lưu |
| corrected_text | Reference thu được bằng first replacement của từng gold edit |
| annotations | Ordered list: start, end, text, label, replacements |
| entities | List: start, end, text, label, valid |
| source | kind, reference, license |

`source.kind`: fixture, authentic, synthetic_rule, synthetic_llm. `source.reference` chỉ tới provenance record hoặc nguồn có thể truy vết. `source.license` là license identifier hoặc trạng thái chưa xác minh; **một chuỗi license không chứng minh có quyền sử dụng**. Data gate chặn nguồn chưa xác minh.

Entity labels: person, place, organization, technology, foreign_term. Valid entities không giao với gold edits; typo trong tên có entity `valid=false`. Empty replacements hợp lệ cho xóa ký tự. Zero-length source spans chỉ dùng character_deletion. Không có grammar/style/punctuation labels trong spelling gold.

First replacement dùng để tái tạo reference chính. Các replacement khác chỉ hợp lệ nếu annotator xác nhận không đổi ý nghĩa trong context. Đây chưa biểu đạt đầy đủ mọi tổ hợp sentence-level alternatives; evaluator phải ghi rõ hạn chế, không dùng một gold string để phủ nhận mọi cách sửa hợp lệ.

## Provenance và split

1. Lưu source snapshot, source license evidence, collection date và document/thread identifiers ngoài record trong versioned manifest.
2. Deduplicate nguồn trước khi split; toàn bộ revisions và augmentations của một nguồn ở cùng split.
3. Freeze split assignments và checksums trước generation. Không học dictionary, tokenizer, frequencies, confusion weights hoặc calibration từ test.
4. Chạy validator với toàn bộ split files. Validator bắt group leakage và NFC/casefold/whitespace exact duplicates giữa source/target texts; **không bắt semantic paraphrases, near duplicates hoặc group IDs khai sai**.
5. Kiểm tra near duplicates và repeated templates riêng. Mỗi holdout có source lineage khác train; unseen-name slice còn cần entity-disjoint split.

## LLM và deterministic synthetic pipeline — specification, chưa triển khai

LLM dùng tạo contextual confusions, hard negatives và teacher labels. Mechanical noise dùng generator kiểm soát được edit trace. Telex/VNI cần mô phỏng một IME behavior đã chỉ định; không coi mọi raw keystroke string là lỗi người dùng thấy trên màn hình. Chỉ kiểm tra committed text, không báo lỗi giữa IME composition.

Manifest generation phải ghi teacher/model version, prompt hash, decoding settings, seed nếu hỗ trợ, clean source hash, operator, severity và review status. Teacher model version/seed không đảm bảo provider tái tạo bit-for-bit; lưu output gốc để replay.

Sinh cả clean negatives, tên lạ đúng, tên có typo thật, regional vocabulary và informal/technical text. Không dùng capitalization làm shortcut duy nhất cho tên. Kiểm tra một mẫu phân tầng bằng người đọc tiếng Việt; teacher confidence chưa được coi là calibrated. Distillation bằng labels/rank preferences là vòng đầu; soft targets chỉ dùng khi teacher có cung cấp và được đánh giá phù hợp.

Không đưa test vào prompts hoặc dùng teacher quyết định lại gold test trong quá trình tuning. Không thể bảo đảm public test chưa từng có trong pretraining của teacher; ghi rõ giới hạn và bổ sung private/authored-after-training challenge cases khi có thể. Không dùng private user messages nếu chưa có sự cho phép và xử lý dữ liệu phù hợp.

## Data acceptance gate

- 100% records qua schema/span reconstruction và cross-split checks.
- Provenance/license review xong cho mọi nguồn được train hoặc redistribute.
- Hai annotators độc lập kiểm tra pilot ít nhất 100 câu, báo span agreement và label disagreements; adjudicate trước freeze gold.
- Challenge, synthetic và naturally occurring errors được báo riêng.
- Gold ambiguous/unresolved không bị ép vào một correction; giữ trong separate review queue.

Examples hiện có là fixture do dự án viết để kiểm tra contract. Không phải independent test, không phải mẫu phân phối lỗi thật.
