# Bài toán: máy cần phát hiện điều gì?

## Mục tiêu bài học

Đọc xong, người học phân biệt spelling với grammar/style, viết được một ví dụ có label và giải thích output cần gì. Đây là problem definition: quy ước để ta biết model đang học nhiệm vụ nào.

Đọc trước [learning guide](learning-guide.md); tra [glossary](glossary.md) khi gặp thuật ngữ mới.

## 1. Input, detection và correction

Input là đoạn text Unicode gốc, có thể gồm tiếng Việt, English, tên riêng và identifiers. R baseline hiện giới hạn 256 raw code points. Đây là giới hạn code của bài hiện tại, không phải lý thuyết ML hoặc yêu cầu mọi model sau này.

Detection hỏi “có lỗi ở đâu?”. Correction hỏi “thay chỗ đó bằng gì?”. Ví dụ “họcc” có chữ c thừa. Với “bóng truyền”, từng âm tiết có thể hợp lệ nhưng context cho thấy khả năng nhầm “bóng chuyền”. Với “deploy service”, đây có thể là code-switching hợp lệ.

Trong bài đầu, không sửa grammar, style, punctuation, nội dung thực tế hoặc viết lại câu cho hay hơn. Nếu người viết có thể định nói nhiều điều khác nhau, không tự gán một ý định chắc chắn.

## 2. Nhóm ví dụ cần phân biệt

| Nhóm | Ví dụ/ý nghĩa | Điều cần học |
|---|---|---|
| Non-word error | “họcc” trong câu học bài | Local character patterns có thể hữu ích |
| Real-word confusion | “chơi bóng truyền” | Dictionary membership chưa đủ; cần context |
| Valid foreign term | “Kubernetes”, “deploy” | Ngoài tiếng Việt chưa đồng nghĩa sai |
| Named entity | Tên người, nơi, công ty | Tên lạ có thể đúng; tên quen cũng có thể có typo |
| Unresolved | “Nguyen” khi không rõ cách viết người đó muốn | Thiếu bằng chứng thì giữ nguyên |

Một spelling label mô tả lỗi đã được xác nhận, không thay thế việc hiểu các nhóm trên. Thông tin entity và spelling có thể cùng tồn tại trên một span: một tên viết sai vẫn là tên.

## 3. Taxonomy: tên gọi các loại lỗi

Taxonomy nghĩa là bảng phân loại. Enum names sau là các giá trị hiện validator chấp nhận; chưa có nghĩa baseline đã nhận diện tốt từng loại.

| Label | Người viết đã làm gì? | Cách biểu diễn edit |
|---|---|---|
| character_insertion | Gõ thừa ký tự | Span ký tự thừa; replacement rỗng để xóa |
| character_deletion | Gõ thiếu ký tự | Span rỗng tại chỗ cần chèn |
| character_substitution | Thay nhầm ký tự | Span cũ và replacement mới |
| character_transposition | Đảo thứ tự | Span chứa các ký tự đảo |
| missing_diacritic | Thiếu dấu | Cụm ký tự có dấu bị ảnh hưởng |
| wrong_diacritic | Sai thanh hoặc dấu nguyên âm | Cụm ký tự cần thay |
| misplaced_diacritic | Đặt dấu trên nguyên âm khác | Span bao các cụm cần đổi |
| input_method | Có căn cứ về lỗi Telex/VNI | Span cần sửa; cần ghi bằng chứng về cause |
| real_word_confusion | Đơn vị hợp lệ bị dùng nhầm trong câu | Minimal span đủ sửa lỗi |

Một edit có thể vừa là substitution về mặt ký tự vừa là real-word confusion về mặt ngôn ngữ. Quy ước v1 ưu tiên input_method khi có bằng chứng, sau đó real_word_confusion, diacritic rồi generic edit. Đây là lựa chọn annotation để nhất quán, có thể nghiên cứu tách thành hai trục operation/cause sau này.

Không suy ra chắc chắn người dùng dùng Telex chỉ từ một chuỗi gần giống Telex. Phân biệt lỗi thực nhìn thấy sau khi bộ gõ commit với trạng thái đang composition.

## 4. Chính sách tiếng Việt

Strict profile yêu cầu dấu trong văn xuôi thông thường, nhưng vẫn chấp nhận tên không dấu khi đó là cách viết hợp lệ. Informal profile có thể chấp nhận text không dấu và slang theo guideline đã chọn. Cùng một input có thể cần label khác nếu policy khác.

Không tự ép mọi spelling variant/vocabulary vùng miền về một cách viết. Không mặc định “Nguyen” là “Nguyễn”. Khi gắn label, ghi rõ context và lý do; examples mơ hồ có thể để ở review queue thay vì ép đáp án.

## 5. Span và Unicode bằng ví dụ

Span là đoạn text từ start đến trước end. Repo dùng zero-based Unicode code-point offsets trên input gốc. Với “Tôi hoc bài.”, chữ o trong “hoc” nằm ở start 5, end 6. Replacement “ọ” sửa một chỗ thay vì rewrite toàn câu.

Missing-character edit dùng start bằng end, vì không có ký tự cũ để xóa. Ví dụ “đag” → “đang” cần chèn n trước g. Với ký tự lặp như “họcc”, có thể có nhiều edit scripts tương đương; guideline cần chọn anchor nhất quán.

NFC/NFD có thể hiển thị cùng chữ nhưng dùng số code points khác nhau. Đừng coi khác normalization là spelling error. Giữ raw text, chuẩn hóa khi cần tính toán và ánh xạ về raw spans. Một grapheme là cụm người đọc nhìn như một ký tự; tránh cắt dấu ra khỏi chữ nền.

Validator v1 kiểm tra bounds, slices và reconstruction; chưa kiểm tra đầy đủ mọi grapheme boundary. Baseline minimal edits hỗ trợ cụm Vietnamese base+combining, chưa phải toàn UAX #29. Đây là bài kiểm tra nâng cao để học thêm, không chặn bài fit model đầu tiên.

## 6. Output và abstention

R baseline hiện trả findings và abstentions riêng. Finding chứa span, label, candidates và score heuristic. Abstention nghĩa giữ nguyên vì chưa đủ bằng chứng. Check không tự rewrite input; apply top suggestion là thao tác riêng.

Một score 0,8 chưa phải “80% đúng”. Baseline chưa có calibrated confidence. Không thấy finding cũng chưa chứng minh toàn câu đúng. Những giới hạn này giúp ta đọc output đúng thay vì tin model vì một con số.

## Bài tập

Chọn 10 câu gồm câu đúng, typo, tên lạ, thiếu dấu và code-switching. Viết label cho các lỗi chắc chắn, đánh dấu trường hợp chưa rõ. Sau đó tự trả lời: cần thêm thông tin gì để phân xử? Có trường hợp nào hai người có thể gắn nhãn khác nhau?

Điểm hoàn thành bài: giải thích được nhiệm vụ, units và một failure case của dictionary. Chưa cần đạt một precision target. Xem [data contract](data-contract.md) để ghi examples và [benchmark](benchmark.md) để chấm chúng.
