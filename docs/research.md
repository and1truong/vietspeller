# Competing architectures và evidence ledger

Không có benchmark results của Vietspeller. Mọi chất lượng kỳ vọng và data volume dưới đây là hypotheses hoặc starting budgets.

| Option | Components | Parameters và budget | Starting training budget | Main hypothesis / failure |
|---|---|---|---|---|
| A, <100 KB | Rules + compressed syllable lexicon + hashed char n-grams + linear detector/ranker | 16–25K learned scalars; ~16–25 KB nếu INT8; toàn bundle 60–95 KB | 10–50K clean source sentences, 50–200K instances; authentic sample nếu được phép | Tốt với local/non-word patterns; real-word context và unknown names có thể giới hạn recall |
| B, <1 MB | Char CNN + one BiGRU layer + character/gap heads + shared candidate ranking | ~60–120K parameters, 240–480 KB FP32; bundle 0,4–0,9 MB | 50–200K source sentences, 0,2–1M pairs | Context giúp confusions; synthetic shortcuts và sequential CPU cost là rủi ro |
| C, <10 MB | 4-layer encoder, d=192, FFN=384, vocab~2.048, span/name/rank heads | ~1,6M parameters, ~6,4 MB FP32; bundle 7–9 MB | 0,2–1M source sentences, 1–5M pairs nếu learning curve còn lợi ích | Rộng context hơn; tiny model từ đầu có thể thiếu ngữ nghĩa và thua hybrid |

Ước lượng phải đếm lại khi có config. A cần INT8 hoặc pruning để giữ đủ chỗ cho lexicon; scale/metadata phải tính. B phải giữ character representations cho span head, không chỉ pooled syllable vector. C cần unknown-character fallback và subword-to-source alignment. Cả ba dùng shared candidate generation để so chất lượng ranker công bằng, nhưng báo end-to-end của từng pipeline riêng.

10 KB là exploratory rules/classifier subset, chưa kỳ vọng đủ toàn phạm vi. 100 KB/1 MB/10 MB là research budgets, không hard success requirements.

## Model family order

Dictionary/rules → hashed Logistic Regression → nếu boundary errors quan trọng, thử budgeted linear-chain CRF. CNN-only là ablation của B; BiGRU cung cấp sentence context. Chỉ so BiLSTM nếu có câu hỏi hoặc failure cụ thể. Transformer C là đối thủ cần đo, không mặc định thắng. Không train mọi family chỉ để đủ danh sách.

Correction bắt đầu bằng generation + contextual ranking + keep-original. Seq2seq chỉ thêm khi candidate recall có giới hạn được chứng minh, hoặc flexible edits mang lợi ích vượt rủi ro rewrite.

Name handling so ba biến thể: rules/allowlist; learned foreignness/name signals; joint heads. Không hard-protect tất cả uppercase/OOV tokens. NER và spelling có thể tương tác hai chiều; phải có names-with-errors slice.

## Open research questions và phép đo

1. Kiến trúc nhỏ nhất hữu ích? Pareto curve recall ở matched false-positive rate, artifact bytes và CPU latency.
2. Rules giảm gánh học bao nhiêu? Rules-on/off ở cùng training budget.
3. Character-only đủ không? Local-only vs contextual features, nhất là real-word slice.
4. NER hay language ID hay rules? So preservation và typo recall, entity-disjoint holdout.
5. Candidate ranking có đủ? Candidate recall@K trước ranker accuracy.
6. Cần bao nhiêu authentic data? Learning curve với 0/100/500/2.000/... authentic examples, cùng synthetic budget và document splits.
7. Synthetic có giống thật? Cross-generator và independent authentic evaluation; so noise distributions và error analysis.
8. Lỗi nào không thể chắc chắn sửa? Adjudicate minimal contrast cases, lưu unresolved khi thiếu intent.
9. Trade-offs CPU? Cùng hardware/thread/length protocol, whole pipeline.
10. Khi nào pretrained tốt hơn? So transfer/student với scratch ở matched artifacts và data; pretrained teacher lớn có thể là offline reference. Chưa có bằng chứng giữ chất lượng khi ép teacher xuống budget.

## Primary sources, checked 2026-10-20

- [Vietnamese tweet normalization and NER](https://link.springer.com/article/10.1186/s40649-016-0032-0): nghiên cứu rules/dictionary/n-grams và Telex/VNI. Evidence cho baseline family; không chứng minh đạt budget A hoặc modern-domain quality.
- [VSEC paper](https://arxiv.org/abs/2111.00640), [original dataset repository](https://github.com/VSEC2021/VSEC): synthetic training và realistic evaluation; 9.341 câu, 11.202 lỗi. Đây là số liệu nguồn, không phải kết quả dự án. README đã xem chưa cho đủ license evidence; verify trước ingest/redistribute. Syllable labels cần audit trước chuyển sang exact character spans.
- [Hierarchical Transformer paper](https://arxiv.org/abs/2105.13578), [Viwiki-Spelling](https://github.com/heraclex12/Viwiki-spelling): repository nêu 107 Wikipedia documents, offsets/suggestions và CC BY 4.0. Verify source/version/license attribution trước dùng. Không dùng cùng nguồn để vừa tune vừa làm independent final test.
- [Unicode UAX #15](https://www.unicode.org/reports/tr15/): canonical equivalence và normalization.
- [Unicode UAX #29](https://www.unicode.org/reports/tr29/): grapheme/text segmentation; không thay thế Vietnamese lexical word segmentation.
- [ONNX Runtime quantization](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html): implementation reference; không bảo đảm speedup cho các model đề xuất.

Engineering hypotheses ở trên khác với established findings từ các nguồn. Không lấy reported metrics của paper làm expected score của tiny model. Không có speculative performance numbers được trình bày như kết quả đo.
