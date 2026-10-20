# Phase 1 — Problem definition, v1

## Mục tiêu và non-goals

Input: một đoạn Unicode gốc, có thể gồm tiếng Việt, English, tên riêng và technical identifiers. Vòng đầu tối đa 256 code points; đoạn dài phải được phân đoạn có offset mapping, không silently truncate.

Output: danh sách spelling findings, mỗi finding có start/end, error label, calibrated confidence khi đã có calibration, tối đa ba candidate replacements và action `suggest` hoặc `abstain`. Mọi span tham chiếu input gốc. Không có finding không đồng nghĩa đã chứng minh câu đúng.

Tách detection và correction. Không đổi văn bản nếu người dùng chỉ gọi detection. Candidate giữ nguyên phải có mặt trong quyết định sửa. Auto-correct chưa thuộc E001; cần gate riêng cho edit precision trước khi bật.

Không sửa grammar, punctuation, style, factual errors hoặc thay cách diễn đạt. Bảo toàn case, whitespace và phần không nằm trong edit. Dùng edit nhỏ nhất đủ biểu đạt lỗi, không rewrite sentence.

## Label taxonomy

| Label | Ý nghĩa theo lỗi người viết | Annotation |
|---|---|---|
| character_insertion | Người viết gõ thừa ký tự | Span ký tự thừa, replacement rỗng |
| character_deletion | Người viết bỏ thiếu ký tự | Zero-length span ở vị trí cần chèn |
| character_substitution | Thay nhầm ký tự | Span bị thay |
| character_transposition | Đảo thứ tự | Span chứa các ký tự đảo |
| missing_diacritic | Thiếu dấu nhưng chưa phải thiếu cả ký tự | Grapheme bị ảnh hưởng |
| wrong_diacritic | Sai thanh hoặc dấu nguyên âm | Grapheme bị ảnh hưởng |
| misplaced_diacritic | Dấu đặt trên nguyên âm khác | Span bao các grapheme bị đổi |
| input_method | Dấu vết lỗi Telex/VNI có căn cứ | Span cần sửa; không suy ra keyboard chỉ từ typo |
| real_word_confusion | Âm tiết/từ hợp lệ nhưng nhầm trong context | Minimal span cần sửa |

Labels dùng thứ tự ưu tiên: input_method nếu có bằng chứng; sau đó real_word_confusion nếu các đơn vị đều hợp lệ; sau đó diacritic; cuối cùng generic character edit. Causal keyboard attribution không thể suy ra chắc chắn từ text đơn lẻ. Future schema có thể tách edit operation và error cause thành hai trục nếu annotation agreement thấp.

Entity annotation độc lập với spelling annotation. `valid=false` nghĩa entity surface có lỗi đã xác nhận; entity vẫn là tên. Tên không thấy trong training không được mặc định sai.

## Chính sách ngôn ngữ

- `strict`: cần dấu trong văn xuôi tiếng Việt thông thường; tên không dấu có thể là cách viết chủ ý, không tự suy ra tên có dấu.
- `informal`: chấp nhận bỏ dấu, slang và code-switching đã được guideline cho phép. Không coi mọi slang là hợp lệ; trường hợp chưa phân xử để ngoài gold cho tới khi adjudicate.
- Biến thể vùng miền và cách đặt dấu được chấp nhận phải có policy version, không tự động ép về một chuẩn.
- Phân biệt invalid Vietnamese syllable, valid syllable sai context, foreign term, named entity và unresolved. Đây là evidence classes, không phải mọi trường hợp đều có thể xác định chỉ từ chuỗi chữ.
- Câu đúng ngữ pháp nhưng khác ý tác giả thường không thể phát hiện chắc chắn. Không gắn gold correction nếu context cho phép nhiều cách hiểu.

## Unicode và spans

Offsets là Unicode code-point indices, zero-based, half-open, trên input gốc. Không phải UTF-8 bytes hoặc UTF-16 code units. Browser adapter phải chuyển đổi rõ ràng, gồm emoji trước vị trí lỗi.

NFC chỉ dùng nội bộ; giữ mapping về input gốc. Canonical equivalence NFC/NFD không phải spelling error. Annotation không cắt giữa extended grapheme cluster. Missing-character edit dùng gap; nếu nhiều edit script tương đương do ký tự lặp, guideline chọn anchor phải nhất quán và evaluator hỗ trợ acceptable gold alternatives.

V1 validator kiểm tra bounds và text slices; **chưa kiểm tra đầy đủ grapheme boundaries hoặc tạo normalization mapping**. Hai việc này là gate trước API production, không được ngầm coi đã hoàn thành.

## Quyết định ban đầu, có thể điều chỉnh bằng bằng chứng

Ưu tiên precision hơn recall cho editor. Threshold chọn bằng validation, không bằng test. Proposed pilot target: precision ≥98%, clean-sentence flag rate ≤1%, valid-entity preservation ≥99,5%. Các tỷ lệ này là mục tiêu nghiên cứu, không phải lời hứa sản phẩm. Auto-correction cần threshold và benchmark riêng.
