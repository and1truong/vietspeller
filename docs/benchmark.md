# Benchmark protocol v1

Protocol là specification; evaluator và benchmark dataset chưa được triển khai. Không báo quality từ fixture.

## Partitions

Development benchmark dùng để khám phá và chọn threshold. Final test là nguồn giữ riêng, chỉ chạy sau khi freeze experiment; nếu phân tích rồi sửa model theo test, tập đó trở thành development và phải có holdout mới.

Pilot development target: 1.000 câu đúng tự nhiên, 500 câu có lỗi thật, 300 challenge cases. Đây là curated composition, không đại diện natural error prevalence. Precision ngoài sản phẩm còn phụ thuộc base rate; cần một stream sample nguyên trạng để đánh giá triển khai.

Slices: non-word, real-word, Telex, VNI, missing/wrong/misplaced marks, multiple errors, no-diacritic passages, unusual vocabulary, regional variants, foreign terms, known/unseen names, names with genuine typos, technical code-switching, NFC/NFD và emoji-before-error offsets. Ghi support của từng slice; không kết luận trên nhóm quá ít mẫu.

Unseen entity: tên surface và canonical aliases không nằm trong train/allowlist; group theo identity nếu biết. Tên viết hoa và viết thường đều cần kiểm tra. Đo việc giữ tên đúng và phát hiện typo trong tên riêng biệt.

## Detection

- Primary: exact character-span precision, recall, F1, one-to-one matching. Wrong type nhưng đúng boundary được tính ở untyped metric; typed metric báo riêng.
- Zero-length gaps phải match đúng anchor. Grapheme-safe alternative gold anchors cần adjudication khi edit script không duy nhất.
- Token-span P/R/F1: tokenizer cố định, versioned, giữ offsets; whitespace-delimited units trong pilot không được gọi là lexical words. Gold gap tại ranh giới dùng gap token, không tự gán tùy ý sang token trái/phải.
- Exact span localization accuracy trên gold-associated findings, kèm mẫu số; không thay thế end-to-end P/R/F1.
- Clean sentence flag rate = số câu gold sạch có bất kỳ finding / số câu gold sạch.
- False positives trên 1.000 clean tokens; không gộp hai FPR definitions.

Abstained candidate không phải detection finding đã xác nhận; nếu UI vẫn gạch chân thì phải tính là finding. Báo precision–recall và risk–coverage curves, không giấu phần abstain.

## Correction

- Candidate recall@K trên gold spans: đáp án đúng có nằm trong candidate set không?
- Oracle-span top-1/top-3: đánh giá ranker khi vị trí lỗi đã biết.
- End-to-end top-1/top-3: lỗi bỏ sót và candidate không sinh được đều là failure; không chỉ chấm lỗi detector tìm thấy.
- Edit precision: đúng bao nhiêu trên tổng edits thực hiện; denominator phải gồm edits sai trên câu sạch.
- Sentence exact match, báo riêng noisy và clean inputs. Chấp nhận curated reference alternatives; không mặc định paraphrase là correction.
- Entity preservation: tỷ lệ valid entities không bị sửa; báo thêm valid-entity flag rate. Một hệ thống không sửa gì có preservation 100%, nên luôn báo cạnh correction/detection recall.

## CPU protocol

Ghi commit, dataset checksum, artifact checksum, Python/library versions, CPU model/architecture, OS, threads, batch size và input lengths. Chạy batch=1, một thread trước; warmup 100 calls, ít nhất 1.000 timed calls. Báo p50/p95, throughput và length buckets. Cold load đo fresh processes, không trộn vào warm latency.

Đo end-to-end: normalization/mapping, features, detector, candidate generation, ranking và output mapping. Giới hạn candidate count phải được log. Báo process peak RSS trong fresh process và baseline runtime riêng. Ghi rõ RSS units phụ thuộc OS; không dùng Python allocation tracker thay cho whole-process RAM.

Disk budget = uncompressed inference artifacts gồm weights/lexicon/tokenizer/tables/configuration. Báo compressed download, runtime dependencies và training checkpoints riêng. Sau pruning/quantization phải chạy lại quality, calibration và latency; nhỏ hơn không tự đảm bảo nhanh hơn.

Confidence intervals: bootstrap theo document/group, không coi các synthetic variants là observations độc lập. Tỷ lệ lỗi rất thấp cần đủ mẫu; pilot chỉ cho tín hiệu ban đầu, chưa chứng nhận production.
