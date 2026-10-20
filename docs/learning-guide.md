# Học Vietspeller từ đầu

## Dành cho ai và cần biết gì trước?

Tài liệu dành cho người biết lập trình nhưng mới học machine learning (ML, học máy). Không yêu cầu đã biết PyTorch, neural network hoặc đại số tuyến tính nâng cao. Biết đọc một hàm, một vòng lặp và một file JSON là đủ để bắt đầu.

Đích đến là tự giải thích được: dữ liệu đi vào đâu, máy học cái gì, kết quả có đáng tin không, và vì sao model train bằng Python vẫn dùng được từ TypeScript/Go. Một model đơn giản nhưng hiểu rõ đáng giá hơn model phức tạp chạy được mà không giải thích được.

## 1. Trước hết: có chương trình chạy chưa có nghĩa đã training

Đọc câu “Tôi đang họcc bài.” Người lập trình có thể tự viết luật tìm một chữ c thừa, rồi đề xuất “học”. Chương trình đó có thể hữu ích nhưng chưa học từ dữ liệu.

Một cách khác là đưa nhiều ví dụ đúng/sai cho thuật toán. Thuật toán điều chỉnh các con số bên trong để dự đoán tốt hơn. Quá trình điều chỉnh đó gọi là training.

Vietspeller hiện có cách thứ nhất: dictionary/rules baseline. Baseline nghĩa là phương án đơn giản để làm mốc so sánh. Chưa có learned weights, tức các con số đã được tối ưu từ training data. Mở JSON vocabulary hiện tại không đồng nghĩa đang xem một neural model đã train.

Tự kiểm tra: thêm “Vietspeller” vào danh sách từ hợp lệ có làm hệ thống học quy luật về các tên chưa từng gặp không? Vì sao?

## 2. Một ví dụ chạy xuyên suốt bài học

Với “Tôi đang họcc bài.”, ta có ba công việc khác nhau:

1. Detection: xác định có lỗi, và lỗi nằm ở chữ c nào.
2. Candidate generation: tạo những cách sửa có thể xảy ra, ví dụ xóa chữ c thừa.
3. Ranking/decision: xếp hạng phương án rồi quyết định đề xuất hay giữ nguyên.

Model phân loại đúng một token là sai vẫn chưa tự biết sửa thành gì. Một danh sách có đáp án đúng cũng chưa bảo đảm đáp án đó được xếp đầu. Vì thế ta học và chấm từng phần riêng.

Đối chiếu với “Tôi chơi bóng truyền.”: “bóng” và “truyền” đều có trong vocabulary. Lỗi này cần context, nghĩa là các từ xung quanh. Đối chiếu tiếp “Tôi đang deploy service.”: từ ngoài tiếng Việt có thể hoàn toàn hợp lệ. “Không biết từ” là một tín hiệu, không phải bằng chứng chắc chắn có lỗi.

## 3. Hệ thống học máy gồm những phần nào?

| Phần | Cách hiểu trong dự án |
|---|---|
| Input | Câu người dùng nhập, giữ nguyên Unicode gốc |
| Dataset | Tập ví dụ dùng để học hoặc kiểm tra |
| Label | Đáp án người hướng dẫn gắn cho một ví dụ |
| Feature | Thông tin từ input được biến thành các con số |
| Model | Quy tắc tính output từ features; một số con số có thể được học |
| Training | Dùng input/labels để điều chỉnh các con số đó |
| Inference | Dùng các con số đã cố định để dự đoán input mới |
| Evaluation | So dự đoán với đáp án tham chiếu để tìm điểm mạnh/yếu |
| Artifact | File lưu weights, vocabulary và cấu hình cần để dùng lại |

Đây là các vai trò, không nhất thiết mỗi vai trò là một thư viện hoặc service riêng.

## 4. Lộ trình đọc và thực hành

| Bài | Đọc | Thực hành | Dấu hiệu đã hiểu |
|---|---|---|---|
| 1 | [Problem definition](problem-definition.md) | Phân loại 10 câu đúng, sai và mơ hồ | Giải thích vì sao không phải từ lạ nào cũng sai |
| 2 | [Rules baseline](rules-baseline.md) | Chạy check rồi theo một ví dụ qua source code | Chỉ ra phần do người viết luật quyết định |
| 3 | [Data contract](data-contract.md) | Đọc và tự viết một record minh họa | Giải thích input, label và span của record |
| 4 | [Training từ đầu](training-from-zero.md) | Tính một prediction bằng weights giả định trên giấy | Phân biệt fit, predict, loss và threshold |
| 5 | [Benchmark](benchmark.md) | Tính TP/FP/FN và đọc R000 | Phân biệt kết quả đúng với kết luận hợp lệ |
| 6 | [E001](../experiments/E001-baseline-feasibility.md) | Viết giả thuyết, rồi học train linear baseline ở bước sau | So model với rules trên dữ liệu được tách đúng |
| 7 | [Research](research.md) | Chọn một failure case và một thí nghiệm phân biệt nguyên nhân | Biết khi nào cần context hoặc neural model |
| 8 | [TypeScript và Go](cross-language-inference.md) | Lần theo features → weights → output ở ngôn ngữ khác | Biết phải mang theo gì ngoài file weights |

Các bài training và port model hiện là hướng dẫn/bài tập sắp thực hiện; repo chưa có training CLI, exported linear model hoặc TypeScript/Go implementation. Những commands trong README chỉ chạy phần đã có.

## 5. Cách mentor và người học làm việc

Trước một bước mới, mentor giải thích kiến thức tối thiểu và nêu câu hỏi cụ thể. Người học dự đoán điều gì sẽ xảy ra, thử thiết kế hoặc chạy bài tập. Sau đó cùng xem code, output và ví dụ model làm sai. Nếu bí, mentor đưa gợi ý dần; nếu yêu cầu full implementation, mentor cung cấp và giải thích.

Không cần đoán đúng. Ví dụ dự đoán dictionary sẽ nhận ra mọi lỗi, rồi gặp “bóng truyền”, là một bước học tốt: ta vừa thấy giới hạn của lexical lookup bằng bằng chứng cụ thể.

Mỗi lần chỉ nên thay một thành phần để biết nguyên nhân. Nếu thay dataset, model và tokenizer cùng lúc rồi score tăng, ta chưa biết phần nào tạo ra lợi ích.

## 6. Dữ liệu nhỏ có dùng được không?

Có. Ta có thể bắt đầu với ví dụ tự viết để hiểu feature extraction và vòng training. Gọi rõ đây là toy exercise: bài tập nhỏ, không đại diện toàn tiếng Việt. Score trên bài tập đó cho biết code hoạt động với bài tập, không cho biết model tốt ngoài đời.

Sau khi hiểu cơ chế, thêm dữ liệu từ nguồn khác và giữ một phần chưa dùng để học. Không cần đợi có hàng triệu câu hoặc một hệ thống production mới được train model đầu tiên.

Giữ riêng một vài ví dụ không nhìn đáp án khi điều chỉnh model là thói quen học đáng giá ngay cả ở quy mô nhỏ. Với benchmark nghiêm túc hơn, ta kiểm tra thêm nguồn, trùng lặp, cách gắn nhãn và độ đa dạng.

## 7. Cách ghi lại điều đã học

Sau mỗi bài, viết năm câu: tôi đang hỏi gì; tôi dự đoán gì; tôi đã thay đổi/chạy gì; tôi quan sát được gì; điều gì vẫn chưa biết. Dùng [report template](../experiments/report-template.md) khi cần ghi đầy đủ hơn.

Không cần học thuộc toàn bộ thuật ngữ ngay. Khi gặp từ mới, tra [glossary](glossary.md), quay lại ví dụ rồi tự nói lại bằng lời của mình.
