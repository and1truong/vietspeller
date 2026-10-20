# Chọn model để học: từ đơn giản đến phức tạp

## Mục tiêu và cách đọc

Hiểu mỗi model family giải quyết câu hỏi nào trước khi chọn kiến trúc. Repo chưa có learned model hoặc independent quality benchmark. Những sizes/data volumes sau là ước lượng thiết kế để đặt câu hỏi; không phải results, guarantees hoặc prerequisites của bài học đầu.

Đọc [training từ đầu](training-from-zero.md) để hiểu features/weights trước. Không cần học hết neural network mới được train Logistic Regression.

## 1. Các họ phương pháp khác nhau thế nào?

| Phương pháp | Ý tưởng đơn giản | Điều học qua thí nghiệm |
|---|---|---|
| Dictionary/rules | Người lập trình viết tiêu chí, tra tập từ | Vì sao OOV không tự động sai |
| Char n-gram + Logistic Regression | Tạo features từ đoạn ký tự rồi học weights | ML thêm gì so với luật và dictionary? |
| CRF | Học labels trên một chuỗi và quan hệ giữa labels | Sequence constraints có giúp boundaries không? |
| Character CNN | Học filters tìm local character patterns | Local patterns có đủ cho typo types nào? |
| GRU/BiLSTM | Đọc chuỗi và dùng thông tin trước/sau | Context thay đổi real-word errors thế nào? |
| Tiny Transformer | Attention kết hợp các phần trong context | Lợi ích có xứng đáng data/size/complexity không? |
| Hybrid | Kết hợp các thành phần với vai trò rõ | Rules giúp phần nào, learned component giúp phần nào? |

Các mô tả này không dự đoán ai thắng. CRF có thể lớn nếu feature dictionary lớn; neural model có thể overfit; dictionary tốt có thể rất mạnh với bài toán hẹp. Đừng quyết định bằng tên kiến trúc.

## 2. Ba hướng cạnh tranh để nghiên cứu dần

| Hướng | Các phần có thể thử | Parameters/size ước lượng, chưa đo | Rủi ro cần quan sát |
|---|---|---|---|
| A: ultra-tiny, mục tiêu thử dưới 100 KB | Rules, lexicon nén, hashed n-grams, linear score/ranker | 16–25K learned scalars; weights INT8 khoảng 16–25 KB; bundle dự kiến 60–95 KB | Context yếu, vocabulary thiếu, hash collisions và unknown names |
| B: small neural, mục tiêu thử dưới 1 MB | Character CNN, một BiGRU layer, span/gap heads | Khoảng 60–120K parameters; FP32 weights 240–480 KB; bundle dự kiến 0,4–0,9 MB | Synthetic shortcuts, data ít, span alignment và sequential CPU cost |
| C: contextual model, mục tiêu thử dưới 10 MB | 4 encoder layers, hidden 192, FFN 384, vocabulary khoảng 2.048, các prediction heads | Khoảng 1,6M parameters; FP32 weights khoảng 6,4 MB; bundle dự kiến 7–9 MB | Thiếu kiến thức dù có attention, tokenizer offsets và training từ đầu |

Parameter là con số có thể học. Một triệu FP32 parameters cần khoảng bốn triệu bytes cho weights, chưa gồm metadata, dictionary hoặc runtime. INT8 có thể giảm weight storage nhưng còn scale/metadata và cần đo lại quality. Không giả sử quantization luôn nhanh hơn.

R baseline hiện có không phải A đã train: nó dùng rules/seed dictionary, không có learned weights. Bundle nhỏ của R000 cũng không chứng minh một full lexicon/context model nằm vừa budget A.

Mốc 10 KB là bài khám phá rules/classifier hẹp; chưa có cơ sở hứa đủ mọi chức năng. Các mốc size là câu hỏi để học trade-offs, không điều kiện thành công.

## 3. Dữ liệu bao nhiêu là đủ?

Chưa có câu trả lời chung trước thí nghiệm. Bắt đầu ít để hiểu pipeline, rồi learning curve: train với các subsets tăng dần, giữ cách đánh giá nhất quán và xem thêm dữ liệu có ích không.

Các budgets từng đề xuất cho A là 10–50K source sentences/50–200K instances; B là 50–200K sources/0,2–1M pairs; C là 0,2–1M sources/1–5M pairs. Đây chỉ là hypotheses cho nghiên cứu lớn hơn. Không cần đạt các con số đó trước toy training. Nhiều examples do một generator lặp template chưa chắc hữu ích bằng ít examples đa dạng.

## 4. Những câu hỏi giúp chọn experiment tiếp theo

1. Rules làm được bao nhiêu? So baseline với và không có một nhóm rules.
2. Local characters có đủ không? Xem non-word errors và real-word errors riêng.
3. Context có ích thật không? So local-only với contextual features trên cùng dữ liệu.
4. Name protection giảm FP nhưng có che typo không? Đọc preservation cạnh entity-typo recall.
5. Generator không có đáp án hay ranker chọn sai? Đo candidate coverage trước ranking.
6. Authentic examples thêm được gì? Giữ synthetic budget rồi thêm từng lượng lỗi thật được kiểm tra.
7. Synthetic bias có tồn tại không? Train bằng một generator, thử nguồn lỗi khác.
8. Có case nào thiếu intent nên không sửa chắc được không? Giữ unresolved thay vì ép label.
9. Model lớn hơn có đáng không? So chất lượng, artifact size và CPU trên cùng điều kiện.
10. Có nên dùng pretrained model? So transfer với scratch khi đã thấy giới hạn; không mặc định model nén giữ nguyên quality của teacher.

Ablation là bỏ một thành phần để hỏi nó có đóng góp gì. Đừng thay ba thứ cùng lúc rồi chỉ nhìn score cuối. Khi thêm context làm tăng feature count, cần ghi đó là hai thay đổi để giải thích comparison công bằng.

## 5. Correction, tên riêng và autocomplete liên quan thế nào?

Candidate generation tạo các cách sửa; ranking dùng evidence để sắp xếp. Nếu đáp án không được tạo ra, ranker giỏi đến đâu cũng không chọn được. Seq2seq là một hướng cho phép sinh text linh hoạt hơn, nhưng tăng bài toán kiểm soát ý nghĩa và minimal edits; chưa cần bắt đầu ở đó.

Name handling có thể thử rules/allowlist, foreignness signals, riêng NER hoặc joint task sau khi hiểu errors. Một từ viết hoa không mặc định đúng, một từ không có trong vocabulary không mặc định sai.

[Personal dictionary ticket](https://github.com/and1truong/vietspeller/issues/2) và [autocomplete ticket](https://github.com/and1truong/vietspeller/issues/3) ghi nhu cầu riêng. Không tự suy ra cần neural model khác hoặc cùng weights. Với autocomplete, phần đang gõ có thể chưa hoàn tất; đừng dùng spelling errors làm đáp án cho tác vụ khác mà không định nghĩa lại labels.

## 6. Facts, hypotheses và suy đoán

Fact của repo: code hiện có xử lý gì, raw reports ghi gì, tests đã chạy gì. Hypothesis: thêm context có thể giúp phân biệt một confusion. Speculation: một tiny Transformer nhất định sẽ đạt chất lượng tốt dù chưa đo; không được trình bày như kết quả.

Bài tập: chọn một hypothesis và viết một counterexample có thể làm nó sai. Sau đó chọn phép thử nhỏ nhất phân biệt được hypothesis với giải thích cạnh tranh.

## Nguồn nghiên cứu và cách đọc, kiểm tra 2026-10-20

- [Vietnamese tweet normalization/NER](https://link.springer.com/article/10.1186/s40649-016-0032-0): tham khảo rules/dictionary/n-grams và Telex/VNI. Không chứng minh budget/quality của A.
- [VSEC paper](https://arxiv.org/abs/2111.00640) và [original dataset](https://github.com/VSEC2021/VSEC): synthetic training cùng realistic evaluation; nguồn nêu 9.341 câu, 11.202 lỗi. Đây là số liệu nguồn, không phải Vietspeller results. License evidence cần được làm rõ trước ingest/redistribute; syllable labels không tự biến thành exact character labels.
- [Hierarchical Transformer paper](https://arxiv.org/abs/2105.13578) và [Viwiki-Spelling](https://github.com/heraclex12/Viwiki-spelling): repository nêu 107 Wikipedia documents, offsets/suggestions và CC BY 4.0. Cần kiểm tra source/version/attribution, không dùng cùng nguồn vừa tune vừa gọi là independent test.
- [Unicode normalization](https://www.unicode.org/reports/tr15/) và [segmentation](https://www.unicode.org/reports/tr29/): hiểu code points/combining marks; không thay thế Vietnamese lexical segmentation.
- [ONNX quantization](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html): tài liệu khi học compression, không phải lời bảo đảm speedup.

Đọc paper sau khi có câu hỏi thực nghiệm; không cần hiểu toàn paper để làm bài rules/linear đầu tiên. Đường từ learned parameters sang app được giải thích ở [cross-language inference](cross-language-inference.md).
