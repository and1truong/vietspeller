# Vietspeller — học machine learning bằng bài toán chính tả tiếng Việt

Vietspeller là dự án học tập dành cho người biết lập trình nhưng rất mới với machine learning, đặc biệt training model. Ta sẽ đi từ một chương trình dùng dictionary/rules đến model nhỏ có thể train, đánh giá, lưu lại và dùng từ Python, TypeScript hoặc Go.

**Mục tiêu là hiểu và tự thực hiện được ML lifecycle, không phải đạt production readiness.** Một thí nghiệm thất bại vẫn có giá trị nếu ta giải thích được vì sao. Tính tái lập và việc chấm đúng giúp học tốt hơn, không phải bộ thủ tục để ngăn người mới bắt đầu.

## Hiện đã có gì?

| Phần | Trạng thái |
|---|---|
| Dictionary/rules baseline | Chạy được bằng Python; luật do người viết chọn, chưa học weights |
| Minimal-edit suggestions | Có; giữ input nguyên và trả vị trí/candidates |
| Dataset validator | Có; kiểm tra cấu trúc, spans và một số dạng trùng giữa splits |
| Evaluator và CPU diagnostic | Có; dùng được để học cách đo và đọc errors |
| Dữ liệu ví dụ | 22 records minh họa và seed vocabulary rất nhỏ |
| Training linear/neural model | Chưa triển khai |
| LLM data generation | Chưa triển khai |
| Exported model, TypeScript/Go inference | Chưa triển khai; có bài giải thích đường đi |
| Personal dictionaries và autocomplete | Chỉ có problem-definition tickets, chưa triển khai |

“Chạy được spell checker” chưa đồng nghĩa “đã train model”. Đọc sự khác biệt này trước khi thử tăng score.

## Bắt đầu từ đâu?

1. [Learning guide](docs/learning-guide.md): giải thích dự án và thứ tự các bài.
2. [Training từ đầu](docs/training-from-zero.md): sample, label, feature, weight, loss, fit và predict là gì?
3. [Rules baseline](docs/rules-baseline.md): chạy phần hiện có và theo một câu qua source.
4. [Data contract](docs/data-contract.md) và [benchmark](docs/benchmark.md): tạo examples và đọc kết quả.
5. [Roadmap học tập](docs/roadmap.md): mốc tiếp theo và cách tự kiểm tra mình đã hiểu.
6. [TypeScript/Go inference](docs/cross-language-inference.md): sau khi train, dùng model từ ngôn ngữ khác thế nào?

Tra [glossary](docs/glossary.md) khi gặp từ mới. Không cần biết hết thuật ngữ trước khi làm bài đầu.

## Thực hành với code hiện có

Cần Python 3.11 trở lên. CLI hiện chỉ dùng Python standard library, chưa cần PyTorch, scikit-learn, GPU hoặc API key. Những lệnh sau chạy từ thư mục gốc repository trên shell hỗ trợ cách đặt PYTHONPATH này, như Bash:

- PYTHONPATH=src python -m vietspeller.cli validate data/examples/illustrative.jsonl
- PYTHONPATH=src python -m unittest discover -s tests -v
- PYTHONPATH=src python -m vietspeller.cli check --artifact data/examples/bootstrap-lexicon.json --text 'Tôi đang họcc bài trên Kubernetes.'
- PYTHONPATH=src python -m vietspeller.cli evaluate data/examples/illustrative.jsonl --artifact data/examples/bootstrap-lexicon.json --split demo --allow-demo

PYTHONPATH=src cho Python biết nơi tìm package của repo. Validate kiểm tra dữ liệu. Unittest chạy các kiểm tra chương trình. Check trả suggestions. Evaluate so suggestions với đáp án minh họa; allow-demo nhắc rằng đây là bài tập, không phải dữ liệu test độc lập.

Với câu check trên, quan sát chữ c thừa và span được trả về. Source text không bị tự động sửa. Mở [hướng dẫn baseline](docs/rules-baseline.md) để giải thích từng field và thử một câu model làm sai.

Có thể cài editable package bằng python -m pip install -e . rồi dùng lệnh vietspeller; việc này đăng ký package/CLI, không thực hiện training. Windows PowerShell đặt environment variable khác Bash; đây là khác biệt cách chạy shell, không phải khác biệt model.

## Bản đồ tài liệu

| Tài liệu | Câu hỏi được giải thích |
|---|---|
| [Problem definition](docs/problem-definition.md) | Ta gọi điều gì là lỗi, và output cần nói điều gì? |
| [Data contract](docs/data-contract.md) | Một example có những fields nào, labels/spans dùng ra sao? |
| [Training](docs/training-from-zero.md) | Máy học những con số nào từ dữ liệu? |
| [Benchmark](docs/benchmark.md) | Precision/recall có nghĩa gì và tính thế nào? |
| [Research](docs/research.md) | Vì sao thử linear model trước neural network? |
| [Rules baseline](docs/rules-baseline.md) | Phần code hiện có thực sự làm gì và chưa làm gì? |
| [E001](experiments/E001-baseline-feasibility.md) | Thí nghiệm học tiếp theo hỏi gì và so sánh ra sao? |
| [R000 report](experiments/R000-smoke-report.md) | Đọc một kết quả đã đo và phân tích failure cases thế nào? |
| [Report template](experiments/report-template.md) | Ghi điều đã học bằng một báo cáo dễ hiểu thế nào? |
| [Cross-language inference](docs/cross-language-inference.md) | Mang weights và preprocessing sang TypeScript/Go thế nào? |
| [Teaching guide](docs/teaching-guide.md) | Mentor, tài liệu và ticket cần phục vụ người mới ra sao? |

## Cách học và giới hạn kết luận

Mỗi bước: hiểu vấn đề → dự đoán → thử làm → chạy → đọc errors → giải thích → chọn câu hỏi tiếp. Mentor đưa gợi ý theo nhu cầu và cung cấp full implementation khi được yêu cầu. Không tự mở rộng thành một hệ thống production.

Có thể bắt đầu training trên bài tập nhỏ tự viết, nhưng phải gọi đúng là toy exercise. Để nói model tổng quát tốt, cần dữ liệu được giữ riêng và cách đánh giá thích hợp. Không biến fixture thành independent test chỉ bằng cách đổi tên split.

Các mốc 10 KB, 100 KB, 1 MB và 10 MB là câu hỏi nghiên cứu để học trade-offs; không phải điều kiện để được tiến sang bài khác. Chưa có chất lượng hoặc latency được cam kết cho ứng dụng thực.

Repo chưa chọn license cho code/project-authored text. Nguồn bên ngoài cần có quyền sử dụng và ghi attribution phù hợp; điều này không ngăn bắt đầu bằng ví dụ tự viết.

## Những ý tưởng được ghi riêng

- [#2 — Personal, project và domain dictionaries](https://github.com/and1truong/vietspeller/issues/2).
- [#3 — Vietnamese autocomplete](https://github.com/and1truong/vietspeller/issues/3).

Hai tickets chỉ lưu context/problem, chưa chốt solution hoặc yêu cầu thực hiện ngay. Chúng không thay thế bài học training model đầu tiên.
