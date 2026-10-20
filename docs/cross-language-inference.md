# Train bằng Python, dùng model từ TypeScript và Go

## Câu trả lời trước

Có thể dùng một model đã train bằng Python từ TypeScript hoặc Go. Thông thường không train lại chỉ vì ứng dụng dùng ngôn ngữ khác. Ta chuyển phần dữ liệu đã học và triển khai hoặc dùng runtime cho phép tính inference.

Ví dụ linear model chỉ cần features, weights, bias và quy tắc quyết định. Neural network thường dùng một graph cùng weights; runtime thực thi graph đó. Ngôn ngữ viết training script không bắt buộc là ngôn ngữ của ứng dụng cuối.

Tài liệu này là bài học và kế hoạch thực hành. Repo hiện có Python rules baseline; chưa có trained linear/neural artifact, ONNX export, TypeScript package hoặc Go package của Vietspeller. Không có lệnh export đã triển khai để chạy ngay.

## 1. Tách ba thứ thường bị gọi chung là “model”

| Thứ | Chứa gì? | Cần khi nào? |
|---|---|---|
| Training code | Đọc examples, tạo features, tối ưu parameters, đo validation | Khi học hoặc train lại |
| Model artifact | Parameters đã học và cấu hình cần để giải thích chúng | Khi load lại để predict |
| Inference engine | Xử lý input, chạy phép tính, tạo output/spans | Mỗi khi ứng dụng cần prediction |

File weights là dữ liệu, không phải chương trình tự chạy. Engine phải hiểu hình dạng và ý nghĩa các con số. Dictionary của R baseline cũng là artifact, nhưng không phải learned weights. Có artifact không chứng minh đã có training.

## 2. Cách dễ hiểu nhất: linear model và một phép tính nhỏ

Sau khi train binary Logistic Regression, giả sử có một vector weights và một bias. Inference tính z = bias + tổng của feature nhân weight tương ứng; rồi tính sigmoid của z. Đó là phép toán có thể viết trong TypeScript hoặc Go mà không cần scikit-learn lúc chạy.

Ví dụ weights giả định [1,2; 2], bias −1 và features [1; 1] cho z = 2,2 và output khoảng 0,900. Đây là phép tính minh họa giống bài training, không phải model đã train trong repo.

Python xuất parameters và cấu hình thành một dạng được mô tả rõ, chẳng hạn JSON cho bài học đầu. TypeScript/Go đọc các con số, tạo đúng feature vector rồi tính cùng công thức. Khi đổi kiểu model, như multiclass classifier hoặc CRF, công thức/decoding phải đổi tương ứng; không dùng sigmoid nhị phân cho mọi model.

Với scikit-learn, cần hiểu class order và ý nghĩa coefficients/intercept của estimator đang dùng trước khi export. Lưu một file pickle/joblib chủ yếu phục vụ Python; nó không tự biến thành model TypeScript/Go đọc được. [Model persistence documentation](https://scikit-learn.org/stable/model_persistence.html) phân biệt rõ hướng dùng lại Python object và hướng inference qua ONNX.

## 3. Phần dễ sai nhất thường là features, không phải phép nhân

Nếu Python học weight thứ 17 cho một n-gram, nhưng Go đặt n-gram đó ở ô 28, weights có thể load đúng mà predictions vẫn sai. Ta phải chuyển cả “cách tạo số”, không chỉ “các số đã học”.

Checklist của bài port linear model:

- Cùng NFC normalization và chính sách viết hoa; Python casefold không mặc định tương đương mọi hàm lowercase của ngôn ngữ khác.
- Cùng đơn vị ký tự và cách tách tokens/ngrams; không vô tình hash UTF-8 byte fragments ở Go trong khi Python dùng Unicode characters.
- Cùng feature index hoặc hash function, encoding, seed, bucket count và sign rule.
- Cùng binary/count features, vector normalization và mọi scaling đã fit.
- Cùng weights, bias, class order, threshold và quy tắc abstain.
- Cùng dictionary/terms khi so whole pipeline; cùng span/candidate tie-breaking nếu muốn output giống nhau.

HashingVectorizer của scikit-learn dùng signed 32-bit MurmurHash3 theo [tài liệu của estimator](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.HashingVectorizer.html). Khi port phải xem chính xác feature analyzer và cách mapping/sign trong phiên bản đã chọn; không thay bằng hash mặc định của language. Hash function giống tên chưa đủ chứng minh toàn feature vector giống nhau.

Bài đầu có thể dùng một vocabulary feature nhỏ, explicit mapping, để nhìn rõ từng con số. Hashing là bài tiếp theo, không phải điều kiện phải giải quyết trước khi hiểu inference.

## 4. Nếu model là neural network: ONNX và runtime

ONNX biểu diễn các phép toán/graph cùng parameters trong một định dạng trao đổi. ONNX Runtime là engine đọc và chạy model tương thích. Đây là hai thứ khác nhau: file định dạng và chương trình thực thi.

[PyTorch có hướng dẫn export model sang ONNX](https://docs.pytorch.org/tutorials/beginner/onnx/export_simple_model_to_onnx_tutorial.html). Export thành công chưa chứng minh toàn pipeline dùng đúng: còn phải so output với Python reference và kiểm tra operators, dtype và input shapes ở runtime đích.

Nhiều model nhận tensors là số hoặc token IDs, không nhận trực tiếp câu tiếng Việt. Custom Python preprocessing không mặc nhiên đi vào graph. Cần ghi rõ phần nào ở ngoài graph: tokenizer, character IDs, padding, normalization, candidates, threshold và span mapping. Một số preprocessing có thể được export khi có hỗ trợ; phải kiểm chứng thay vì đoán.

PyTorch state_dict chủ yếu là weights; một chương trình khác còn cần kiến trúc và các quy ước để diễn giải weights. ONNX là một lựa chọn cho graph inference, không phải mọi model/checkpoint đều được chuyển tự động và giữ nguyên behavior.

## 5. TypeScript có hai môi trường khác nhau

| Môi trường | Lựa chọn để học | Điều phải kiểm tra |
|---|---|---|
| Node.js | Viết linear inference bằng TypeScript; hoặc dùng onnxruntime-node cho model ONNX | Native runtime/platform support, tensor shapes, preprocessing |
| Browser | Linear inference bằng JavaScript/TypeScript; hoặc onnxruntime-web | Runtime assets, operator/backend support, memory và UI responsiveness |

ONNX Runtime có [Node.js binding](https://onnxruntime.ai/docs/get-started/with-javascript/node.html) và [Web runtime](https://onnxruntime.ai/docs/get-started/with-javascript/web.html). Browser và Node không mặc định có cùng backend/operators hoặc packaging. CPU/offline là mục tiêu bài học: cần đóng gói hoặc chuẩn bị model/runtime assets sẵn; không dựa vào một dịch vụ LLM qua mạng.

Với model đơn giản, tự viết vài phép tính giúp hiểu inference. Với neural graph nhiều operators, runtime thường giúp ta tập trung vào preprocessing/output thay vì tự viết lại toàn neural network. Đây là lựa chọn học tập theo độ phức tạp, chưa phải architecture decision cuối.

## 6. Go sẽ gọi model thế nào?

Với linear model, Go có thể đọc parameters và tự tính score/sigmoid. Điều này cho phép học một đường inference bằng Go mà không cần Python process hoặc neural runtime.

Với ONNX, Go cần binding hoặc cầu nối tới runtime. Tại lần kiểm tra tài liệu 2026-10-20, repository Microsoft ONNX Runtime có [Go module](https://github.com/microsoft/onnxruntime/tree/main/go), và [package docs](https://pkg.go.dev/github.com/microsoft/onnxruntime/go/onnxruntime) mô tả Go bindings cho C API, cùng việc load native shared library. Module hiện không nên được mặc định là API v1 ổn định; kiểm tra commit/version, go.mod, platform và native library compatibility khi thực sự làm bài.

[go.mod được kiểm tra](https://github.com/microsoft/onnxruntime/blob/main/go/go.mod) khai báo Go 1.26 tại thời điểm đọc; ví dụ này cho thấy runtime/binding có yêu cầu toolchain riêng. Khi học inference linear thuần Go, ta không cần thêm dependency ONNX chỉ để thực hiện phép tính linear.

[C API chính thức](https://onnxruntime.ai/docs/get-started/with-c.html) là nền tảng tham khảo để hiểu session, tensors và native runtime. Không mặc định một binding bất kỳ dùng cgo, pure Go hoặc hỗ trợ mọi cross-compilation target; xem implementation/version đã chọn. “Có Go binding” không đồng nghĩa model ONNX chạy bằng một Go binary không có native dependency.

Một phương án học khác là TypeScript/Go gọi Python inference process qua một local interface. Ta giữ nguyên Python behavior để học tích hợp trước; đổi lại vẫn cần Python runtime và chi phí giao tiếp. Local process có thể hoạt động offline. Đây là lựa chọn khác với port inference, không phải bắt buộc và chưa được triển khai ở repo.

## 7. Đừng bỏ qua Unicode offsets

Với câu “🙂 hoc”, vị trí chữ o khác nhau nếu đếm theo các đơn vị khác nhau:

| Cách đếm trên input gốc | Start | End, không gồm vị trí này |
|---|---:|---:|
| Python code points, contract của Vietspeller | 3 | 4 |
| JavaScript UTF-16 code units | 4 | 5 |
| Go UTF-8 byte offsets | 6 | 7 |
| Go rune/code-point offsets | 3 | 4 |

Emoji trước chữ h có một code point, hai UTF-16 units và bốn UTF-8 bytes. Không đưa trực tiếp code-point offset của Python vào string slicing của JavaScript hoặc Go bytes.

Go range trả byte index kèm rune, không tự trả ordinal rune index; xem [Go strings, bytes and runes](https://go.dev/blog/strings). Go có [Unicode normalization package](https://pkg.go.dev/golang.org/x/text/unicode/norm). JavaScript strings dùng UTF-16 code units theo [ECMAScript specification](https://tc39.es/ecma262/multipage/ecmascript-data-types-and-values.html#sec-ecmascript-language-types-string-type).

NFD còn có thể tách một chữ có dấu thành nhiều code points. Mapping về raw input phải được kiểm tra riêng với model score. Dự đoán đúng nhưng highlight lệch vẫn là bug của spelling feature. Bài đầu dùng giới hạn rõ và test case nhỏ, chưa cần giải quyết toàn bộ Unicode/IME để học phép tính linear.

## 8. Parity test: chứng minh hai implementation làm cùng việc

Parity nghĩa là cho Python và ngôn ngữ đích cùng input rồi đối chiếu từng bước. Một bộ tham chiếu nhỏ nên gồm câu đúng, typo, tên có dấu, tên nước ngoài, NFC/NFD, emoji trước lỗi và input có nhiều candidates.

Thứ tự debug:

1. Normalized input và token boundaries có giống không?
2. Features/IDs có giống không, bao gồm sparse indices và sign?
3. Raw model scores có gần nhau trong tolerance đã chọn không?
4. Label/class order, threshold và candidates có cho cùng quyết định không?
5. Spans trên raw text và suggested output có giống không?

Floating-point có thể sai khác nhỏ theo dtype và thứ tự phép tính. Chọn tolerance trước khi chấm, đồng thời xem cases gần threshold; số gần nhau vẫn có thể tạo quyết định khác ở boundary. Quantization là bài riêng: INT8 cần scale/zero-point phù hợp và phải đo lại parity/quality, không chỉ đổi file extension.

Nếu features khác nhau, debug preprocessing trước khi retrain. Nếu Python đã sai, một port chính xác có thể cũng sai: parity đo tính tương đương implementation, không đo linguistic quality. Hai bài kiểm tra đều cần thiết nhưng trả lời hai câu hỏi khác nhau.

## 9. File nào cần đi cùng ứng dụng?

Với bài linear: parameters, feature specification/mapping, class order, threshold/policy, dictionary nếu pipeline cần, phiên bản/schema và các golden parity cases. Với neural model: graph/weights, tokenizer/character vocabulary, tensor specification và runtime dependencies phù hợp, cộng postprocessing giống Python.

JSON dễ đọc cho bài đầu nhưng có overhead. File nhỏ không đồng nghĩa toàn app ít RAM; Python interpreter, Node/native runtime và ONNX shared library đều có chi phí riêng. Ta sẽ đo để hiểu trade-off sau khi đã có output đúng, chưa cần tối ưu byte đầu tiên.

## 10. Bài thực hành dự kiến, chưa triển khai

1. Tự tính một toy linear prediction bằng các con số giả định ở bài trước.
2. Sau khi train linear model thật bằng Python, export parameters và feature contract.
3. Viết inference một input ở TypeScript và Go, so với Python.
4. Cố ý đổi feature order hoặc cách đếm offsets, quan sát parity test bắt lỗi.
5. Khi có neural model, học export ONNX và so runtime outputs riêng.

Điểm hoàn thành bài học: giải thích được vì sao không cần train lại khi đổi language, cái gì cần được export, cái gì phải port và cách tìm lỗi khi output khác. Chưa yêu cầu publish SDK, deploy server hoặc đạt production SLA.
