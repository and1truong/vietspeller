# Roadmap học tập và các mốc tự kiểm tra

## Cách dùng roadmap

Đây là lộ trình học, không phải production delivery plan. Mỗi mốc có câu hỏi, bài tập và cách tự giải thích lại. Không phải xin phê duyệt cho mỗi mốc và không cần model tốt mới được học bài kế tiếp.

Hiện có R baseline, validator, evaluator và R000 diagnostic. Chưa có learned model, training CLI, authentic benchmark độc lập hoặc TypeScript/Go port. Tài liệu training/export mô tả kiến thức và bài tập dự kiến, không giả vờ các phần đó đã triển khai.

## Lộ trình chính

| Mốc | Câu hỏi học tập | Bài thực hành nhỏ | Hoàn thành khi có thể giải thích |
|---|---|---|---|
| 0. Hiểu chương trình hiện tại | Rules khác training ở đâu? | Theo câu “họcc” qua baseline | Vì sao sửa một luật chưa phải fit weights |
| 1. Định nghĩa bài toán | Cái gì là lỗi, mơ hồ hoặc từ hợp lệ? | Phân loại 10 câu và viết labels | Vì sao tên lạ hoặc chữ không dấu chưa chắc sai |
| 2. Chuẩn bị dữ liệu | Sample, label, split và span là gì? | Viết vài records; cố ý tạo lỗi validator | Vì sao dữ liệu qua validator vẫn có thể gắn nhãn sai |
| 3. Training đầu tiên | Model thay những con số nào? | Tính toy prediction; sau đó học fit linear classifier | Feature, weight, bias, loss và predict khác nhau thế nào |
| 4. Đọc kết quả | Model có học hay chỉ nhớ? | Tính TP/FP/FN và xem errors trên phần giữ riêng | Vì sao training score cao chưa đủ |
| 5. Thí nghiệm so sánh | Learning thêm gì so với rules? | E001 từng variant và một ablation nhỏ | Thành phần nào tạo lợi ích, bằng chứng ở đâu |
| 6. Correction và names | Đúng vị trí đã đồng nghĩa sửa đúng chưa? | Chấm candidates và tên đúng/tên có typo riêng | Vì sao giữ mọi tên có thể bỏ sót lỗi thật |
| 7. Tiny ML nếu cần | Context hoặc neural architecture giải quyết khoảng trống nào? | Chọn một failure class rồi thử model phù hợp | Vì sao cần model đó thay vì chỉ theo trào lưu |
| 8. Dùng từ TypeScript/Go | Parameters đã học được mang đi đâu? | Export linear artifact và làm parity exercise khi có model | Preprocessing, weights, runtime và offsets phải khớp thế nào |
| 9. Tổng kết | Kiến trúc nào đáng giữ cho bài toán này? | Viết experiment report và limitations | Đánh đổi giữa chất lượng, kích thước và độ phức tạp |

Tên riêng cần được quan sát từ mốc đầu; mốc 6 chỉ là lúc học đo chúng kỹ hơn. Personal dictionaries/autocomplete ở issues #2/#3 là nhánh học mở rộng, chưa có quyết định thứ tự triển khai.

## Bắt đầu nhỏ rồi tăng độ nghiêm túc

Toy exercise có thể dùng vài chục examples tự viết để hiểu fit/predict. Giữ một phần để thử input khác và gọi đúng giới hạn. Không đợi có corpus lớn, nhiều annotators hoặc hạ tầng deploy mới được học training.

Khi muốn kết luận rộng hơn, tăng mức kiểm tra: nguồn có quyền sử dụng, labels rõ, source groups không trùng train/test, đánh giá riêng lỗi thật và lỗi sinh ra. Khi dữ liệu đủ, hai người đọc một mẫu để tìm điểm bất đồng là bài học tốt; con số 100 câu trong kế hoạch cũ là một gợi ý nâng cao, không điều kiện bắt đầu.

Các mục tiêu cũ precision 98%, clean flag rate 1% và preservation 99,5% chỉ có thể dùng như ví dụ đặt operating point ở bài nâng cao. Chưa là yêu cầu sản phẩm, chưa là điều kiện “qua phase”. Baseline yếu nhưng được đo và giải thích đúng vẫn hoàn thành một bài học.

## Tái lập ở mức phù hợp

Ban đầu lưu examples, config, command và output. Khi có nhiều runs, thêm commit, hashes, seed và environment. Chỉ thêm công cụ khi nó giúp trả lời một câu hỏi; không cần dựng experiment platform ngay.

10 KB/100 KB/1 MB/10 MB là các mốc để học size accounting và compression. Tối ưu inference sau khi đã có prediction được hiểu rõ. Dùng được từ ngôn ngữ khác là bài học application integration, không yêu cầu publish SDK hoặc production deployment.

## Bước học hiện tại

Đọc [learning guide](learning-guide.md), thử baseline rồi làm bài tính tay trong [training-from-zero](training-from-zero.md). Khi bắt đầu code training, cùng chuẩn bị toy dataset có tên rõ, ghi predictions trước khi chạy và review kết quả. [E001](../experiments/E001-baseline-feasibility.md) đi từng phần, không thực hiện toàn bộ model families trong một lần.

Mentor hỗ trợ theo [teaching guide](teaching-guide.md). Những phần chưa hiểu là tín hiệu để chia bài nhỏ hơn, không phải lý do chạy tiếp code mà bỏ qua giải thích.
