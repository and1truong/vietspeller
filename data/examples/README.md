# Dữ liệu minh họa: đồ dùng cho bài học đầu tiên

## Hai files này dùng để làm gì?

Illustrative.jsonl chứa 22 câu do dự án viết để kiểm tra data contract và inference/evaluator. Bootstrap-lexicon.json chứa 138 syllables cùng 18 protected terms/phrases làm vocabulary nhỏ cho rules baseline.

Chúng được viết phục vụ cùng bài diagnostic, không độc lập với nhau. Không phải authentic corpus, training dataset hoàn chỉnh hoặc final test của tiếng Việt. Một seed vocabulary rất nhỏ giúp nhìn rõ cơ chế và cũng cố ý bộc lộ nhiều giới hạn.

## Cần quan sát gì?

Có clean prose, tên đúng, foreign/technical terms, informal no-diacritic text, extra/missing/substituted characters, Telex/VNI traces, real-word confusion, typo trong tên công nghệ, multiple errors, NFC/NFD và emoji trước vị trí lỗi.

Một label thể hiện intent của ví dụ đã chọn, không chứng minh chuỗi đó luôn sai ở mọi context. Ví dụ “Nguyen” có thể là tên hợp lệ không dấu. Validator không thay thế người đọc tiếng Việt để phân xử.

## Bài tập đọc dữ liệu

1. Tìm record extra-character, kiểm tra chữ c ở offsets 12–13 rồi tự tạo corrected_text.
2. Tìm một clean record: annotations rỗng nghĩa gì?
3. So entity valid true với entity có typo và valid false.
4. Tìm NFD example và giải thích vì sao raw character count có thể khác chữ nhìn thấy.
5. Mở seed vocabulary, tìm một từ đúng chưa có; dự đoán baseline có thể làm gì.

Đọc [data contract](../../docs/data-contract.md) để biết fields và [rules baseline](../../docs/rules-baseline.md) để chạy. Fixtures bị khóa ở split demo; cần --allow-demo khi evaluate để không nhầm diagnostic với independent benchmark.

## Có dùng để học training được không?

Có thể học cách đọc input/label và suy nghĩ về features từ chúng. Repo chưa có training CLI. Khi làm toy training, chuẩn bị bài tập riêng và ghi mục đích rõ; không đổi fixture thành train/test rồi báo generalization score.

Chưa có third-party corpus được import. Project-authored text chưa được chọn license. Khi mở rộng nguồn, ghi provenance/quyền sử dụng và attribution phù hợp; dùng examples tự viết giúp bắt đầu học mà không phụ thuộc một corpus lớn.
