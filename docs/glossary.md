# Từ điển thuật ngữ cho người mới

Đây là tài liệu tra cứu, không phải danh sách cần học thuộc trước khi bắt đầu. Ví dụ đều gắn với Vietspeller; xem [learning guide](learning-guide.md) để biết thứ tự học.

## Dữ liệu và bài toán

| Thuật ngữ | Nghĩa đơn giản | Ví dụ |
|---|---|---|
| Machine learning, ML | Dùng dữ liệu để học các tham số cho một quy tắc dự đoán | Học mẫu ký tự hay xuất hiện trong typo |
| Sample / example | Một đơn vị dữ liệu | Một câu kèm các lỗi đã gắn nhãn |
| Dataset | Tập các examples | Các câu dùng để train và đánh giá |
| Label / annotation | Đáp án hoặc ghi chú người hướng dẫn gắn vào example | Chữ c cuối của “họcc” là thừa |
| Ground truth / gold | Đáp án tham chiếu dùng để chấm; vẫn có thể gắn sai | Gold edit xóa chữ c |
| Clean / noisy pair | Văn bản tham chiếu và phiên bản có lỗi | “học” và “họcc” |
| Synthetic data | Dữ liệu được tạo ra có chủ đích | Sinh câu lỗi bằng chương trình hoặc LLM |
| Authentic data | Dữ liệu xuất hiện trong sử dụng thực, không chỉ do generator tạo | Lỗi thực được người đọc xác nhận |
| Fixture | Ví dụ cố định để kiểm tra chương trình | 22 records minh họa trong repo |
| Negative example | Trong bài toán phát hiện lỗi: ví dụ không có lỗi | Tên lạ nhưng đúng; “negative” không nghĩa chất lượng thấp |
| Real-word error | Từ/âm tiết hợp lệ nhưng dùng nhầm trong context | “bóng truyền” khi định nói “bóng chuyền” |
| Non-word error | Chuỗi không được chấp nhận như đơn vị tiếng Việt trong context đó | “họcc” trong câu học bài |
| OOV | Out of vocabulary: không có trong vocabulary đang dùng | Một tên mới; chưa chắc là lỗi |
| Named entity / NER | Tên thực thể / tác vụ nhận diện tên thực thể | Người, nơi chốn, công ty |
| Code-switching | Trộn ngôn ngữ trong cùng đoạn | “deploy service lên AWS” |

## Model và training

| Thuật ngữ | Nghĩa đơn giản |
|---|---|
| Rule / heuristic | Quy tắc do người lập trình chọn, chưa chắc được học từ dữ liệu |
| Baseline | Phương án đơn giản làm mốc so sánh |
| Feature | Một thông tin được biểu diễn bằng số để model xử lý |
| Feature vector | Danh sách số mô tả một input; thứ tự các số rất quan trọng |
| Character n-gram | Một đoạn n ký tự liên tiếp; “học” có các bigrams “họ”, “ọc” |
| Parameter / weight | Con số bên trong model có thể được training điều chỉnh |
| Bias / intercept | Hằng số cộng vào điểm dự đoán, kể cả khi features bằng 0 |
| Hyperparameter | Lựa chọn của người làm thí nghiệm, như số features hoặc learning rate |
| Fit / training | Tối ưu parameters bằng dữ liệu học |
| Inference / predict | Tính dự đoán cho input mới khi parameters đã cố định |
| Loss | Số đo mức không phù hợp giữa prediction và label trong quá trình học |
| Optimizer | Thuật toán chọn cách cập nhật parameters để giảm loss |
| Gradient | Thông tin về chiều thay đổi của loss khi thay parameters |
| Learning rate | Mức độ lớn/nhỏ của bước cập nhật trong các optimizer dùng khái niệm này |
| Batch | Nhóm examples xử lý cùng một lượt |
| Epoch | Một lượt đi qua training set; không đồng nghĩa mọi iteration của mọi solver |
| Overfitting | Học quá sát train data nên làm kém trên ví dụ mới |
| Underfitting | Model/features chưa mô tả được quan hệ cần học ngay cả trên train data |
| Regularization | Cách hạn chế model học quá phức tạp; không tự bảo đảm hết overfitting |
| Embedding | Vector số đại diện ký tự/token, thường được học |
| Pretrained model | Model đã được học trước trên dữ liệu khác |
| Fine-tuning | Tiếp tục điều chỉnh một pretrained model cho tác vụ/dữ liệu mới |
| Distillation | Dùng output/labels của teacher để học student nhỏ hơn; teacher không mặc định luôn đúng |
| Tensor / shape | Mảng số / kích thước theo các chiều của mảng đó |

## Kiểm tra và so sánh

| Thuật ngữ | Nghĩa đơn giản |
|---|---|
| Train split | Phần dữ liệu dùng để học parameters |
| Validation split | Phần dùng để chọn cấu hình hoặc threshold |
| Test / holdout | Phần giữ riêng để kiểm tra sau khi đã chốt lựa chọn |
| Data leakage | Thông tin từ phần cần giữ riêng vô tình được dùng khi học/chọn model |
| TP / FP / FN | Lỗi báo đúng / báo nhầm / bỏ sót |
| Precision | Trong những lỗi báo ra, bao nhiêu là lỗi thật? |
| Recall | Trong những lỗi thật, bao nhiêu được tìm thấy? |
| F1 | Một cách kết hợp precision và recall; chưa biểu đạt mọi chi phí sử dụng |
| Threshold | Mức điểm để quyết định có báo lỗi không |
| Calibration | Kiểm tra/điều chỉnh để điểm xác suất phù hợp với tần suất đúng thực tế |
| Abstention | Chưa đủ bằng chứng, giữ nguyên thay vì khẳng định một correction |
| Candidate / ranking | Phương án có thể đúng / xếp thứ tự các phương án |
| Top-K | Xem đáp án đúng có trong K phương án đầu không |
| Oracle-span evaluation | Cho sẵn vị trí lỗi đúng để kiểm tra riêng phần tạo/xếp candidates |
| Ablation | Bỏ một thành phần để xem thành phần đó thực sự đóng góp gì |
| Slice | Nhóm examples có đặc điểm chung, như tên riêng hoặc thiếu dấu |
| Support | Số examples/sự kiện phía sau một tỷ lệ |
| Confidence interval | Khoảng biểu diễn bất định của một ước lượng; chưa được evaluator hiện tại tính |

## Unicode và chạy ở ngôn ngữ khác

| Thuật ngữ | Nghĩa đơn giản |
|---|---|
| Token | Đơn vị tokenizer chọn; trong repo thường là một letter unit, chưa chắc là từ ghép |
| Code point | Một đơn vị mã Unicode; không luôn trùng một ký tự nhìn thấy |
| Grapheme cluster | Một cụm code points người đọc có thể nhìn như một ký tự |
| NFC / NFD | Hai dạng chuẩn hóa Unicode có thể biểu diễn cùng chữ có dấu khác nhau |
| Span / offset | Vùng văn bản / vị trí bắt đầu và kết thúc vùng đó |
| Half-open interval | Gồm vị trí bắt đầu, không gồm vị trí kết thúc |
| Artifact | File chứa dữ liệu/cấu hình cần để dùng lại model |
| Checkpoint | Bản lưu trạng thái training; có thể gồm weights và optimizer state |
| Export | Chuyển model sang dạng phù hợp môi trường inference khác |
| Runtime | Chương trình/thư viện thực thi phép tính của model |
| ONNX | Định dạng trao đổi graph/phép toán và parameters của nhiều loại model |
| Quantization | Biểu diễn số với ít bit hơn; cần đo lại sai lệch và tốc độ |
| FP32 / INT8 | Số thực 32-bit / số nguyên 8-bit; weights INT8 còn cần thông tin scale thích hợp |
| Latency | Thời gian xử lý một yêu cầu |
| Throughput | Số yêu cầu xử lý được trong một khoảng thời gian |
| p50 / p95 | Mốc mà khoảng 50% / 95% lần đo có thời gian không lớn hơn nó |
| RSS | Bộ nhớ resident của cả process; không phải chỉ phần weights |
| Parity test | Cho các implementation cùng input để kiểm tra output có tương đương không |

Tự kiểm tra: dùng một example để giải thích sự khác nhau giữa feature, parameter và hyperparameter; giữa loss và F1; giữa artifact và runtime.
