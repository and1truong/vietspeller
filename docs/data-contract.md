# Dữ liệu học: đọc và viết một example

## Mục tiêu bài học

Hiểu một sample chứa input và đáp án như thế nào, đọc được JSONL đang có và biết validator kiểm tra điều gì. Contract là quy ước các fields để code đọc dữ liệu nhất quán, không phải bằng chứng dữ liệu đúng về ngôn ngữ.

Bắt đầu bằng ví dụ tự viết nhỏ. Các yêu cầu kiểm tra nguồn/split nghiêm túc hơn phục vụ kết luận rộng sau này; không cần corpus lớn trước khi hiểu sample/label.

## 1. JSONL là gì?

JSONL là file text UTF-8, mỗi dòng chứa một JSON object đầy đủ. Vì mỗi record độc lập, ta có thể đọc từng dòng và báo vị trí record sai. Mở [illustrative.jsonl](../data/examples/illustrative.jsonl) để xem 22 examples có thật trong repo.

Một record có text gốc, corrected_text làm đáp án chính, annotations mô tả các edits và entities mô tả tên/foreign terms. Câu sạch có annotations rỗng và corrected_text giống text. Empty list là thông tin “không có gold error”, không phải thiếu dữ liệu.

## 2. Các fields v1

| Field | Giải thích cho người đọc mới |
|---|---|
| schema_version | Phiên bản quy ước, hiện là integer 1 |
| id | Tên duy nhất của example |
| group_id | Nhận diện nguồn gốc chung để các biến thể không bị tách qua train/test |
| split | Vai trò dữ liệu: demo, train, validation hoặc test |
| profile | Chính sách strict hoặc informal |
| domain | Loại nội dung, ví dụ general, technical, chat |
| text | Câu gốc, không tự đổi Unicode khi lưu |
| corrected_text | Câu tạo bởi first replacement của từng gold edit |
| annotations | Danh sách gold edits theo thứ tự source offsets |
| entities | Danh sách spans người/nơi/tổ chức/công nghệ/foreign term |
| source | Loại nguồn, reference và thông tin license |

Source kind nhận fixture, authentic, synthetic_rule hoặc synthetic_llm. Fixture là ví dụ cố định của bài kiểm tra; authentic là dữ liệu sử dụng thực; hai synthetic kinds là ví dụ được tạo bằng chương trình hoặc LLM. Loại source do người chuẩn bị khai báo; validator không tự chứng minh khai báo đó đúng.

## 3. Theo một edit cụ thể

Record extra-character có text “Tôi đang họcc bài.” Chữ c thừa ở start 12, end 13. Annotation text là “c”, label là character_insertion và replacements có một chuỗi rỗng. Applying edit nghĩa xóa đoạn đó; corrected_text thành “Tôi đang học bài.”

Tên label mô tả lỗi người viết: insertion là người viết đã gõ thừa, còn thao tác sửa là xóa. Với character_deletion, người viết thiếu chữ nên thao tác sửa là chèn vào span rỗng. Đây là chỗ dễ đảo nghĩa khi mới đọc.

Một annotation có thể có nhiều replacements được người gắn nhãn xác nhận hợp lệ. Replacement đầu tạo corrected_text chính. Không tự thêm paraphrases làm đáp án và không mặc định mọi tổ hợp alternatives tạo cùng một ý nghĩa ở cấp câu.

## 4. Entity không đồng nghĩa miễn mọi lỗi

Entity gồm start, end, text, label và valid boolean. Labels hiện có person, place, organization, technology và foreign_term. Valid true nghĩa surface đã được xác nhận đúng và gold edits không được sửa bên trong nó. Valid false cho phép ghi typo thật trong một tên, ví dụ “Pyhton” khi context xác nhận định viết Python.

Giữ entity labels khi đánh giá không có nghĩa đưa gold entities cho detector. Gold là đáp án để chấm. Cho model xem vị trí/tên đúng từ test sẽ đổi bài toán và có thể làm kết quả quá dễ.

## 5. Train, validation, test khác demo thế nào?

Train dùng để tối ưu weights. Validation dùng để chọn cấu hình/threshold. Test giữ riêng để kiểm tra lựa chọn đã chốt. Demo chỉ minh họa cách chương trình xử lý dữ liệu.

Validator khóa source fixture ở split demo. Đừng đổi 22 fixtures thành test để trình bày independent evaluation. Có thể học training bằng toy examples riêng, nhưng phải đánh dấu rõ mục đích và giới hạn; chưa phải benchmark tổng quát tiếng Việt.

Group_id phải bao source document/thread và mọi derived examples liên quan. Nếu lấy một câu sạch sinh 10 typo variants, giữ chúng cùng split. Chia dòng ngẫu nhiên có thể đưa gần như cùng một câu vào cả train và test, làm ta tưởng model tổng quát tốt.

## 6. Validator đang bắt những lỗi gì?

- Thiếu/không đúng field types, enum không được hỗ trợ hoặc id trùng.
- Span ngoài input, annotation text không khớp raw slice, edits chồng nhau.
- Corrected_text không bằng kết quả áp dụng first replacements.
- No-op edit hoặc chỉ đổi canonical normalization mà gọi là lỗi.
- Gold edit chạm entity được ghi valid true.
- Group_id hoặc text trùng sau NFC/casefold/whitespace normalization xuất hiện ở splits khác nhau.

Nó chưa hiểu semantic correctness, không kiểm tra đầy đủ graphemes, không nhận ra mọi near-duplicate/paraphrase, không biết group_id có được khai thật và không xác nhận license. Cấu trúc đúng chỉ là bước đầu.

Chạy tất cả split files cùng một invocation để kiểm tra trùng giữa files: PYTHONPATH=src python -m vietspeller.cli validate PATH1 PATH2. PATH1/PATH2 là placeholders cần thay bằng file thật, không phải files có sẵn trong repo.

## 7. Tạo dữ liệu tổng hợp để học

Noisy/clean pair là câu lỗi và câu tham chiếu. Deterministic generator có thể chèn/xóa/đổi ký tự và lưu lại edit trace. LLM có thể đề xuất contextual errors hoặc hard negatives: từ lạ nhưng đúng mà classifier dễ báo nhầm.

Cả hai là kế hoạch chưa triển khai. LLM output không mặc định đúng hoặc giống lỗi người thật. Teacher–student distillation là dùng labels/outputs của teacher để học student nhỏ; student có thể học cả lỗi và thiên lệch của teacher. Lưu input/output gốc để xem lại, không chỉ tin một confidence do teacher tự nói.

Ở bài đầu, tự viết một vài examples sẽ giúp hiểu labels hơn sinh hàng triệu câu. Khi mở rộng, lưu source hash, generator/model/prompt version, seed nếu hỗ trợ, operations và review status. Tách nguồn trước khi sinh variants; không để test xuất hiện trong prompts/tuning.

Telex/VNI có trạng thái composition. Raw keystrokes không phải lúc nào cũng là text người dùng đã commit. Khi học generator, phải nêu rõ behavior đang mô phỏng thay vì mặc định một quy tắc cho mọi bộ gõ.

## 8. Khi muốn dữ liệu đáng tin hơn

Ghi provenance, tức nguồn gốc có thể truy vết: nguồn nào, phiên bản nào, có quyền dùng thế nào. Dữ liệu công khai chưa tự động có quyền train/redistribute. Repo hiện chưa import third-party corpus và chưa chọn project license.

Nhờ hai người đọc một mẫu giúp tìm bất đồng trong guideline; đây là bài nâng cao, không bắt buộc hai annotators trước toy training. Giữ ambiguous examples trong review queue thay vì ép gold. Báo riêng synthetic, challenge tự viết và lỗi tự nhiên.

## Bài tập

1. Đọc record extra-character và tự tạo corrected_text bằng span.
2. Viết một clean example và một missing-character example cho bài tập của mình.
3. Cố ý dịch start một vị trí, chạy validator và đọc message.
4. Viết một trường hợp qua validator nhưng label sai về ngôn ngữ.
5. Giải thích vì sao source/target gần trùng giữa train/test làm kết quả dễ gây hiểu nhầm.

Điểm hoàn thành: đọc được một record, hiểu label/span và nói được validator làm được/chưa làm được gì. Bước tiếp theo là [training](training-from-zero.md) và [evaluation](benchmark.md).
