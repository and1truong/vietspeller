# Model học như thế nào? Bài đầu tiên trước neural network

## Mục tiêu và trạng thái

Sau bài này, người học có thể mô tả một vòng training, giải thích model lưu lại cái gì và vì sao loss giảm chưa chứng minh model dùng tốt. Chưa cần tự tính đạo hàm neural network.

Đây là hướng dẫn cho bước học tiếp theo. Repo hiện chưa có lệnh train, learned weights hoặc training dataset độc lập. Các weights và phép tính minh họa dưới đây đều giả định để học toán, không phải kết quả Vietspeller đã đo.

## 1. Chọn một bài toán nhỏ hơn trước

Tạm hỏi: một token có cần được xem xét như typo không? Label 1 nghĩa có lỗi đã xác nhận, label 0 nghĩa hợp lệ trong context đó. Bài tập đầu chỉ phân loại; chưa hứa định vị exact character span, sửa đúng tên hoặc hiểu toàn câu.

Ví dụ “họcc” trong câu học bài có label 1. “học” có label 0. “Kubernetes” có label 0 trong một câu công nghệ. “hoc” có thể có label khác tùy policy và context: đừng đưa examples mơ hồ vào bài đầu rồi giả vờ label là chắc chắn.

Nếu chỉ đưa typo để train, model có thể học mẹo báo mọi token là sai. Vì vậy ta cần cả examples có lỗi và examples đúng, gồm những từ lạ nhưng hợp lệ.

## 2. Đưa văn bản thành số: feature extraction

Model số học không nhận trực tiếp ý nghĩa của chữ “họcc”. Người lập trình phải mô tả input bằng features, hoặc chọn một kiến trúc học biểu diễn từ ký tự/token.

Để dễ tính trên giấy, thử hai features thủ công:

- x1 bằng 1 nếu token không có trong dictionary đang dùng, ngược lại bằng 0.
- x2 bằng 1 nếu có ký tự lặp đáng nghi theo một luật đơn giản, ngược lại bằng 0.

Với dictionary có “học”, “họcc” có thể được biểu diễn thành [1, 1]. Đây là danh sách số, gọi là feature vector. Hai features này cố ý đơn giản và có nhiều lỗ hổng; không phải thiết kế cuối cùng. “Kubernetes” không có trong dictionary tiếng Việt cũng có x1 bằng 1 nhưng không sai.

Tự kiểm tra: tìm một từ đúng có ký tự lặp; giải thích vì sao x2 không được xem là đáp án.

Sau khi hiểu ví dụ này, thử character n-grams: các đoạn ký tự liên tiếp. “học” có các bigrams “họ” và “ọc”. Vectorizer chuyển sự xuất hiện của các đoạn đó thành số. Hashing là một cách đưa nhiều features vào số lượng ô cố định; hai features khác nhau có thể rơi cùng ô, gọi là collision.

## 3. Logistic Regression tính prediction ra sao?

Trong bài toán nhị phân này, model gán một weight cho mỗi feature, cộng thêm bias. Đầu tiên tính điểm z bằng bias cộng tổng của mỗi feature nhân weight tương ứng. Sau đó sigmoid chuyển z thành một số giữa 0 và 1, dùng làm ước lượng xác suất label 1.

Sigmoid của z bằng 1 chia cho (1 + e mũ âm z), với e là hằng số khoảng 2,71828. Đây là công thức tính output ở ví dụ, không phải toàn bộ thuật toán học weights. Training sẽ tìm weights/bias; inference chỉ dùng lại chúng để tính z và sigmoid.

Ví dụ giả định: w1 = 1,2; w2 = 2; bias = −1. Input [1, 1] cho z = −1 + 1,2 + 2 = 2,2. Sigmoid của 2,2 xấp xỉ 0,900. Input [0, 0] cho z = −1, sigmoid xấp xỉ 0,269.

Con số này chưa chứng minh prediction đúng 90% trong sử dụng thực; calibration và dữ liệu đánh giá vẫn quan trọng. Đặc biệt score hiện tại của rules baseline dùng công thức edit heuristic khác, không phải Logistic Regression hoặc calibrated probability.

Weights là phần model có thể học. Định nghĩa features, số ô hashing và cách chia dữ liệu là lựa chọn của người làm thí nghiệm. Sau training, có thể thay threshold quyết định mà không thay weights; không được chọn threshold bằng cách dò final test.

## 4. Model biết dự đoán sai bằng cách nào? Loss

Loss là số đo dùng trong training để phạt predictions không phù hợp labels. Với binary cross-entropy, khi label là 1, model dự đoán 0,8 có loss khoảng 0,223; dự đoán 0,1 có loss khoảng 2,303. Đây là phép tính lý thuyết minh họa: prediction càng tự tin sai càng bị phạt mạnh.

Loss không giống F1. Loss cung cấp tín hiệu để điều chỉnh parameters. F1 đếm các quyết định đúng/sai sau khi chọn threshold và còn phụ thuộc cách chấm spans. Ta có thể thấy training loss giảm mà validation F1 không tăng.

## 5. Vòng training gồm những việc gì?

1. Chuẩn bị examples và labels; xác định mỗi sample là token hay sentence.
2. Chuyển input thành features theo quy ước cố định.
3. Khởi tạo parameters hoặc tiếp tục từ một checkpoint có chủ đích.
4. Tính predictions trên training data.
5. Tính loss so với training labels.
6. Optimizer dùng thông tin tối ưu hóa, thường liên quan gradients, để cập nhật parameters.
7. Lặp lại và theo dõi kết quả trên validation, không cập nhật parameters từ validation labels.
8. Chốt một cấu hình/checkpoint, lưu parameters và cấu hình features.

Với scikit-learn LogisticRegression, thao tác fit thực hiện tối ưu hóa bên trong. Không cần viết PyTorch backward hoặc một epoch loop để dùng estimator này. Iterations của solver không được mặc định gọi là epochs. Khi học PyTorch sau, ta sẽ nhìn rõ forward, loss, backward và optimizer step.

## 6. Chia dữ liệu để kiểm tra việc học

Train là tài liệu được dùng để học parameters. Validation giúp chọn cấu hình và threshold. Test là một phần được giữ riêng để hỏi: những lựa chọn đã chốt có hoạt động trên examples mới không?

Bài tập nhỏ có thể bắt đầu bằng vài chục examples tự viết để hiểu cơ chế. Gọi đó là toy exercise, không phải benchmark tiếng Việt. Chưa cần hàng triệu câu hoặc hai người gắn nhãn mới được học vòng fit đầu tiên.

Tuy vậy, đừng tạo typo từ một câu rồi để bản đúng vào train và bản typo gần giống vào test. Model có thể nhớ source thay vì học quy luật tổng quát. Giữ mọi biến thể của cùng một nguồn ở một nhóm khi split.

Các records demo trong repo được validator cố ý giữ ở split demo. Không đổi fixture thành train/test để làm như đã có dữ liệu độc lập. Khi làm toy training, chuẩn bị bài tập riêng và ghi rõ nguồn, mục đích và giới hạn; khi cần kết luận tổng quát, chuyển sang dữ liệu tách nguồn tốt hơn.

## 7. Đọc biểu hiện học tốt và học sai

| Quan sát | Một giả thuyết có thể kiểm tra tiếp |
|---|---|
| Train tốt, validation kém | Overfitting, nguồn khác nhau hoặc leakage/split chưa được hiểu |
| Train và validation đều kém | Features/model chưa đủ, labels có vấn đề hoặc training chưa phù hợp |
| Synthetic test tốt, authentic test kém | Noise generator không giống lỗi thật |
| Names được giữ nhưng typo names không phát hiện | Protection đổi recall lấy preservation |
| Python tốt, Go khác | Có thể là preprocessing/export bug, chưa chắc phải retrain |

Đây là giả thuyết, không phải chẩn đoán tự động. Xem examples cụ thể và thay một yếu tố để kiểm tra.

Ví dụ hai samples có cùng feature vector nhưng labels đối lập: chỉ điều chỉnh weights không thể làm cả hai luôn đúng với cùng deterministic classifier. Cần thông tin phân biệt hơn, sửa label policy hoặc chấp nhận abstention; không phải cứ train lâu hơn là giải quyết được.

## 8. Những gì phải lưu sau training

Với linear model: weights, bias, thứ tự classes và cấu hình feature extraction. Nếu dùng learned vocabulary, lưu mapping feature → index. Nếu dùng hashing, lưu chính xác thuật toán, encoding, số buckets và quy tắc dấu/normalization. Lưu threshold nếu đã chọn.

Lưu thêm nguồn/split/version dữ liệu, cấu hình training, phiên bản thư viện và report. Random seed giúp giảm một số nguồn ngẫu nhiên nhưng không tự bảo đảm bit-for-bit trên mọi môi trường.

Checkpoint phục vụ tiếp tục training có thể chứa optimizer state. Inference thường không cần optimizer, labels của training set hoặc toàn bộ training corpus. Dictionary, tokenizer và policy cần dùng khi inference vẫn phải đi kèm model.

## 9. Một model phân loại chưa hoàn thành spell checker

Classifier có thể cho biết token đáng nghi. Để trở thành spelling feature, vẫn cần xác định span trên text gốc, tạo candidates, xếp hạng, giữ tên/terms hợp lệ và quyết định abstain khi thiếu bằng chứng. Đó là lý do ta đánh giá cả từng thành phần lẫn toàn pipeline.

Cùng weights có thể dùng được từ Python, TypeScript hoặc Go khi các bước này được chuyển đúng. Đọc tiếp [cross-language inference](cross-language-inference.md), không cần train lại chỉ vì đổi ngôn ngữ ứng dụng.

## 10. Bài tập và điểm tự kiểm tra

1. Viết một example có label 0 nhưng x1 bằng 1. Model có thể nhầm thế nào?
2. Tính z và sigmoid cho [0, 1] với weights giả định ở trên; khoảng 0,731 là giá trị tham khảo của phép tính này.
3. Giải thích vì sao báo mọi token là sai có thể đạt recall cao nhưng precision kém.
4. Vẽ bằng lời các bước từ một câu đến feature vector, prediction và gold comparison.
5. Liệt kê thứ gì thay đổi khi fit; thứ gì chỉ được đọc khi predict.
6. Nếu giảm threshold làm recall tăng, vì sao chưa thể nói model đã “học tốt hơn”?

Kết quả học cần đạt: nói lại vòng training bằng lời của mình, tự tính một prediction nhỏ và đọc được một bảng kết quả. Chưa cần đạt một score sản phẩm hoặc tối ưu RAM.

## Nguồn để đọc sau khi hiểu ví dụ

- [scikit-learn LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html): estimator và learned coefficients/intercept.
- [HashingVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.HashingVectorizer.html): cách biểu diễn features bằng hashing; cấu hình phải được giữ khi inference.
- [Model persistence](https://scikit-learn.org/stable/model_persistence.html): lưu model và dùng lại mà không train từ đầu.
