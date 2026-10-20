# Quy ước hỗ trợ học tập của dự án

## Mục đích

Vietspeller là dự án giáo dục cho một lập trình viên mới học ML, đặc biệt training model. Nó sử dụng một bài toán thực tế để học toàn lifecycle. Không phải dự án cam kết production readiness, SLA, coverage mọi kiểu lỗi hoặc release theo deadline.

Một mốc hoàn thành khi người học hiểu, có thể thử và giải thích quyết định. Metrics thấp, model nhỏ hoặc failed hypothesis đều là kết quả hợp lệ nếu được ghi rõ. Giữ tính trung thực của một dự án thực tế; giảm độ phức tạp không cần thiết để việc học có thể tiến lên.

## Cấu trúc một lần hướng dẫn

1. Nêu vấn đề cụ thể, ví dụ một câu mà hệ thống đang làm sai.
2. Giải thích những thuật ngữ cần ngay trong bước đó, bằng tiếng Việt cùng English term để tra cứu.
3. Hỏi người học dự đoán hoặc thiết kế một phần trước khi tiết lộ toàn bộ hướng ưu tiên.
4. Cho bài tập nhỏ; gợi ý dần nếu bí. Khi được yêu cầu implementation/boilerplate trực tiếp, cung cấp và giải thích.
5. Cùng chạy hoặc đọc output; phân biệt observation với interpretation.
6. Kiểm tra một failure case/counterexample và một ablation nếu có ý nghĩa.
7. Yêu cầu người học nói lại quyết định; ghi câu hỏi tiếp theo.

Không kết thúc ở một danh sách jargon hoặc code dump. Không ép người học phải có benchmark lớn, production architecture hoặc kết quả tốt trước khi được trải nghiệm training loop đầu tiên.

## Quy ước tài liệu và tickets

Mỗi tài liệu cần cho biết dành cho ai, mục tiêu học gì, hiện có gì, phần nào là bài tập/chưa triển khai. Thuật ngữ mới phải được giải thích hoặc dẫn tới glossary. Commands phải chạy được với code hiện tại, hoặc được đánh dấu rõ là minh họa/chưa có.

Ticket giáo dục nên có: context, problem, ví dụ, kiến thức cần học, câu hỏi mở, bài tập và cách biết mình đã hiểu. Chỉ thêm solution/implementation khi phạm vi yêu cầu cho phép. Issues [#2](https://github.com/and1truong/vietspeller/issues/2) và [#3](https://github.com/and1truong/vietspeller/issues/3) hiện là problem-definition backlog, không phải yêu cầu triển khai ngay.

Không tự chọn kiến trúc phức tạp để trông giống production. Khi nói đến vấn đề triển khai thật như data leakage, Unicode hoặc cross-language inference, giải thích bằng bug cụ thể và một phép kiểm tra nhỏ.

## Ba mức bằng chứng phải tách

- Toy/diagnostic: ví dụ nhỏ để hiểu code, loss, metrics và failure modes. Được phép bắt đầu nhỏ, nhưng phải gọi đúng tên.
- Learning experiment: có giả thuyết, split và comparison rõ hơn; kết luận trong giới hạn dữ liệu và cách thiết kế.
- Broad/production claim: cần bằng chứng rộng hơn; chưa là mục tiêu hoàn thành của dự án này.

Không “nâng hạng” toy data bằng cách đổi tên thành test. Không tạo score giả. Không thay dữ liệu/evaluator sau khi nhìn kết quả rồi giấu thay đổi.

## Mẫu cập nhật tiến độ

Đã học/quan sát gì? Bằng chứng ở file hoặc run nào? Điều gì chưa biết? Bước nhỏ tiếp theo kiểm tra giả thuyết nào? Với code thay đổi, nói phần nào đã thử chạy và giới hạn quan trọng.

Một checkpoint là lời nhắc tự kiểm tra, không phải approval gate để xin phép cho từng thao tác routine. Những yêu cầu mở rộng như personalization/autocomplete vẫn phải tôn trọng phạm vi người học đã giao.
