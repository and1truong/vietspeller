# Báo cáo bài thực hành — mã và tên bài

Trạng thái: dự kiến / đang làm / đã làm / chưa đủ bằng chứng.

Dùng mẫu này để ghi điều đã học. Có thể bắt đầu bằng một trang ngắn; chưa cần điền mọi phần nâng cao. Thay các lời hướng dẫn bằng nội dung thật, không điền số liệu giả. Xem [R000](R000-smoke-report.md) để đọc một report có kết quả thực.

## 1. Tôi muốn hiểu điều gì?

Viết một câu hỏi cụ thể, một ví dụ gây khó và lý do câu hỏi có ích. Ví dụ: dictionary bỏ sót lỗi giữa hai syllables hợp lệ; thêm context có thay đổi được không?

## 2. Tôi dự đoán điều gì trước khi chạy?

Ghi hypothesis, lý do và một counterexample có thể làm nó sai. Hypothesis là phỏng đoán có thể kiểm chứng, không phải kết luận. Nếu chưa viết trước khi chạy thì nói rõ, không giả vờ đã preregister.

## 3. Tôi đã dùng gì và làm gì?

Ghi examples/nguồn dữ liệu, toy hay authentic, labels, train/validation/test roles, dictionary và policy. Mô tả model/features và phần nào do người lập trình chọn, phần nào được training học.

Ghi command/config để replay. Với bài lớn hơn thêm commit, hashes, seed, library versions và hardware. Phân biệt một thay đổi duy nhất với nhiều thay đổi cùng lúc; ghi chúng nếu chưa kiểm soát được.

## 4. Tôi quan sát được gì?

Báo số đếm, mẫu số và metrics đã thực sự đo. Detection và correction là hai phép đo khác nhau. Chia synthetic/authentic/challenge khi có. Metric chưa đo ghi “chưa đo”; tỷ lệ không xác định không đổi thành 100%.

Latency/RAM/size chỉ thêm khi đã chạy phép đo phù hợp. Không bắt buộc tối ưu speed trong bài training đầu tiên. Nếu report model size, nói có gồm dictionary/tokenizer/runtime hay chưa.

## 5. Ví dụ nào đúng, ví dụ nào sai?

Chọn một vài examples để xem input, gold, prediction và reason. Tìm FP (báo nhầm), FN (bỏ sót), candidate không có đáp án hoặc ranking sai. Nếu có names, xem cả tên đúng bị sửa và typo trong tên bị bỏ sót.

Không cần đủ 30 examples nếu bài tập nhỏ. Không sửa từng example rồi giấu việc đã nhìn vào test. Nếu thêm dictionary entries sau khi review, đó là run mới với điều kiện khác.

## 6. Tôi giải thích kết quả thế nào?

Tách observation (điều đã đo) khỏi inference (giải thích có thể đúng) và speculation (ý tưởng chưa kiểm chứng). Model có thể học generator shortcut, thiếu feature hoặc gặp label mơ hồ; viết phép thử phân biệt thay vì kết luận chắc ngay.

Nếu có ablation, nói thành phần nào được bỏ, phần nào giữ nguyên và kết quả có thật sự cho phép quy lợi ích cho thành phần đó không.

## 7. Tôi có thể kết luận điều gì và chưa thể kết luận gì?

Viết giới hạn dữ liệu, số mẫu, source overlap và assumptions. Toy score cao chưa đủ chứng minh tốt trên tiếng Việt; parity giữa languages chưa đủ chứng minh model đúng về ngôn ngữ.

Thất bại có được giải thích và ghi lại vẫn hoàn thành một bài học. Không cần đổi mục tiêu để làm report đẹp.

## 8. Bước nhỏ tiếp theo và câu hỏi tự kiểm tra

Nêu experiment rẻ nhất để kiểm tra điều chưa rõ. Viết lại bằng lời của mình: tôi đã hiểu thêm gì về dữ liệu, training hoặc inference? Nếu không trả lời được, quay lại ví dụ thay vì chỉ chạy thêm model lớn.
