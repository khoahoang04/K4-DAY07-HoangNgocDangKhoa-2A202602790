# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hoàng Ngọc Đăng Khoa (MSSV: 2A202602790)
**Nhóm:** G51 (Lớp K4-L3A)
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> 
- Độ tương tự cosine cao (tiến gần về 1) biểu thị hai vector chỉ cùng 
một hướng trong không gian embedding, nghĩa là hai đoạn văn bản có sự 
tương đồng lớn về mặt ngữ nghĩa hoặc cấu trúc từ vựng, không phụ thuộc 
vào độ dài ngắn của câu

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chú mèo đang ngủ lười trên chiếc sofa."
- Câu B: "Con mèo nằm ngủ say trên ghế sô-pha."
- Tại sao tương đồng: Cả hai câu sử dụng các từ đồng nghĩa gần như hoàn 
toàn ("chú mèo" - "con mèo", "sofa" - "ghế sô-pha") và diễn đạt cùng một 
chủ thể, hành động và ngữ cảnh, khiến các vector đại diện của chúng chỉ 
về cùng một hướng

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chú mèo đang ngủ lười trên chiếc sofa."
- Câu B: "Thị trường chứng khoán hôm nay ghi nhận mức tăng kỷ lục."
- Tại sao khác: Hai câu thuộc hai miền chủ đề hoàn toàn độc lập 
(thú cưng/sinh hoạt đối lập với tài chính/kinh tế), không chia sẻ ngữ 
cảnh hay trường từ vựng tương đương, tạo nên hai vector gần như vuông 
góc nhau (cosine similarity gần bằng 0)

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> 
Cosine similarity được ưu tiên hơn khoảng cách Euclid vì các ý chính sau:
- Không bị đánh lừa bởi độ dài của câu
- Không gian nhiều chiều làm khoảng cách Euclid mất tác dụng
- Dễ chuẩn hóa và tính toán siêu nhanh

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> - *Trình bày phép tính:*
>   - Bước nhảy (step) giữa hai chunk: $\text{step} = \text{chunk\_size} - \text{overlap} = 500 - 50 = 450 \text{ ký tự}$.
>   - Số lượng chunk = $\lceil \frac{\text{độ\_dài} - \text{overlap}}{\text{chunk\_size} - \text{overlap}} \rceil = \lceil \frac{10000 - 50}{500 - 50} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22.111... \rceil = 23$.
> - *Đáp án:* **23 chunks** (đã kiểm chứng trùng khớp thực tế với `FixedSizeChunker` trong repo).

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước nhảy giảm còn $500 - 100 = 400$ ký tự, số chunk tăng lên thành $\lceil \frac{10000 - 100}{400} \rceil = \lceil \frac{9900}{400} \rceil = \lceil 24.75 \rceil = \mathbf{25\text{ chunks}}$ (tăng thêm 2 chunks). Chúng ta muốn độ chồng chéo lớn hơn để bảo toàn tính liền mạch ngữ cảnh tại các ranh giới cắt, giúp các thực thể quan trọng hay mệnh đề quy định không bị ngắt đôi giữa hai chunk, từ đó vector embedding giữ trọn vẹn ngữ nghĩa để mô hình truy xuất chính xác hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi sử dụng biểu thức chính quy Lookbehind `r"(?<=[.!?])(?:\s+|\n+)"` để tách câu ngay sau các ký tự kết thúc câu (`.`, `!`, `?` hoặc ngắt dòng) mà vẫn giữ nguyên dấu câu gắn liền với câu trước, tránh lỗi nuốt dấu câu làm câu bị cụt. Sau đó, gom các câu thành từng nhóm gồm `max_sentences_per_chunk` câu và loại bỏ khoảng trắng thừa bằng `strip()`. Xử lý ngoại lệ đầu vào rỗng an toàn bằng cách trả về `[]`, đồng thời ghi nhận hạn chế (edge case) đã biết: các từ viết tắt (*TS.*, *v.v.*) hoặc số thập phân (*3.14*) sẽ bị regex nhận nhầm là điểm kết thúc câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán được thiết kế theo cơ chế hai chiều: **đệ quy xuống sâu** (nếu mảnh cắt bởi separator hiện tại vẫn vượt quá `chunk_size`, tiếp tục gọi `_split` với separator có mức ưu tiên nhỏ hơn theo thứ tự `["\n\n", "\n", ". ", " ", ""]`) và **gom lên** (ghép nối các mảnh nhỏ liền kề kèm separator chừng nào tổng độ dài còn $\le \text{chunk\_size}$ để tránh sinh ra các mẩu vụn 5–10 ký tự). Trường hợp cơ sở (base cases) gồm 3 điều kiện dừng: text rỗng trả về `[]`, text có độ dài $\le \text{chunk\_size}$ trả về chính nó `[current_text]`, hoặc khi danh sách separator cạn (`remaining_separators == []` hoặc `sep == ""`) thì fallback cắt theo lát cắt độ dài cố định `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> - *Lưu trữ:* Tôi sử dụng danh sách trong bộ nhớ (`self._store`) để lưu trữ các record đã chuẩn hóa thông qua helper `_make_record`. Mỗi record lưu một bản sao sâu (`deepcopy`) của metadata, đảm bảo luôn có khóa `doc_id` và vector embedding được tính toán trước bởi `embedding_fn`.
> - *Tính độ tương tự:* Trong hàm `_search_records`, truy vấn được chuyển thành vector qua `embedding_fn`, sau đó tính độ tương tự Cosine với từng embedding trong store bằng hàm `compute_similarity` (hoặc dot product khi vector đã chuẩn hóa độ dài), sắp xếp kết quả giảm dần theo điểm số và trả về `top_k` phần tử (đã loại bỏ trường embedding để làm sạch dữ liệu đầu ra).

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> - *Lọc trước (Pre-filtering):* Tôi áp dụng cơ chế lọc trước: trước khi tính tương đồng vector, hệ thống chỉ giữ lại các record mà mọi cặp key-value trong `metadata_filter` đều khớp chính xác với `record["metadata"]`. Nếu áp dụng lọc sau (post-filtering), $k$ vị trí có thể bị chiếm hết bởi các tài liệu sai tiêu chí dẫn tới trả về danh sách rỗng dù store vẫn có tài liệu hợp lệ.
> - *Cách xóa:* Hàm duyệt toàn bộ danh sách và loại bỏ tất cả record có `record["id"] == doc_id` hoặc `record["metadata"]["doc_id"] == doc_id`. Trả về `True` nếu số lượng record sau khi xóa giảm đi, ngược lại trả về `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> - *Xử lý an toàn:* Kiểm tra nếu store rỗng hoặc kết quả tìm kiếm không có chunk nào thì trả về thông báo lịch sự ngay, không gọi LLM để tiết kiệm tài nguyên.
> - *Cấu trúc prompt & Ngữ cảnh:* Truy xuất `top_k` chunk, đánh số thứ tự từng đoạn ngữ cảnh theo định dạng `[1] (Nguồn: source / doc_id): ...` và đưa vào prompt cùng câu hỏi. Prompt thiết lập các ràng buộc nghiêm ngặt: chỉ sử dụng ngữ cảnh được cung cấp, nói rõ khi không tìm thấy thông tin và bắt buộc trích dẫn số thứ tự nguồn `[1]`, `[2]` để đáp ứng tiêu chuẩn truy vết nguồn gốc (Source Traceability).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================================ test session starts ============================================
platform win32 -- Python 3.11.4, pytest-9.1.1, pluggy-1.6.0 -- D:\lab-VinAI\K4-DAY07-HoangNgocDangKhoa-2A202602790\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\lab-VinAI\K4-DAY07-HoangNgocDangKhoa-2A202602790
collected 42 items                                                                                           

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                  [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                           [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                    [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                     [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                          [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED          [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                 [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED               [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                 [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                 [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                            [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                        [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                  [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED         [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED             [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED       [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED             [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                 [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                   [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                     [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                           [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                  [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED      [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                   [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                            [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                           [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                      [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                  [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED             [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                 [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                       [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                 [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED            [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED           [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED          [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED   [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================================ 42 passed in 0.09s =============================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42


---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|:---:|-------|-------|:-------:|:------------:|:-----:|
| 1 | Thủ tục đăng ký mượn sách thư viện | Quy trình mượn tài liệu tại thư viện PTIT | cao | 0.6166 | Đúng |
| 2 | Sinh viên được mượn tối đa 5 cuốn sách | Hạn mức mượn tài liệu của sinh viên là 5 cuốn | cao | 0.8692 | Đúng |
| 3 | Giờ mở cửa thư viện vào buổi sáng | Ký túc xá đóng cửa lúc 22h đêm | thấp | 0.2086 | Đúng |
| 4 | Trời hôm nay nắng đẹp và nhiều mây | Học phần trí tuệ nhân tạo có 3 tín chỉ | thấp | -0.0662 | Đúng |
| 5 | Cán bộ giảng viên được mượn 10 cuốn sách trong 30 ngày | Sinh viên được mượn 5 cuốn sách trong 14 ngày | cao | 0.7449 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất nằm ở **Cặp 5**: dù hai câu áp dụng cho hai đối tượng bạn đọc khác nhau (cán bộ/giảng viên vs sinh viên) với các hạn mức và số ngày hoàn toàn trái ngược (10 cuốn / 30 ngày đối lập với 5 cuốn / 14 ngày), điểm tương đồng ngữ nghĩa thực tế lại rất cao (0.7449). Điều này chứng minh rằng mô hình embedding nắm bắt ngữ nghĩa chủ yếu ở tầng cấu trúc chủ đề và ngữ cảnh từ vựng (cùng nói về việc mượn sách thư viện, số lượng và thời gian) chứ không tự phân biệt được các ràng buộc logic hoặc phân tách đối tượng chặt chẽ. Đây chính là lý do vì sao trong hệ thống RAG thực tế, ta bắt buộc phải sử dụng cơ chế lọc siêu dữ liệu (`metadata_filter={"audience": "..."}`) để tránh việc truy xuất nhầm quy chế giữa các nhóm đối tượng.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src` (sử dụng `RecursiveChunker(chunk_size=350)` kết hợp `LocalEmbedder`). **5 câu hỏi này trùng khớp với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên khóa mới đăng nhập hệ thống tài liệu số thư viện với mật khẩu mặc định là gì? *(có filter `audience: student`)* | `student-library-borrowing#0`: Thông báo mượn tài liệu và hướng dẫn tra cứu tài liệu số trên phần mềm Dspace... | 0.6575 | Có (Relevant - Top 1) | Mật khẩu mặc định là `123456`, tên đăng nhập là mã sinh viên viết thường. |
| 2 | Mượn tài liệu kho mở về nhà đối với sinh viên và cán bộ giảng viên có thời hạn tối đa bao nhiêu ngày? | `library-rules#19`: Quy định đối với sinh viên hệ chính quy (tối đa 02 cuốn, 07 ngày) và cán bộ, giảng viên (03 cuốn, 15 ngày)... | 0.7540 | Có (Relevant - Top 1) | Sinh viên được mượn 02 cuốn trong 07 ngày; cán bộ giảng viên được mượn 03 cuốn trong 15 ngày. |
| 3 | Thời gian sử dụng máy tính tại phòng truy cập Internet của thư viện được quy định thế nào? | `library-rules#13`: Nội quy phòng truy cập Internet, quy định mỗi máy tính chỉ 01 người sử dụng, thời gian tối đa... | 0.7059 | Có (Relevant - Top 1) | Mỗi máy tính chỉ 01 người sử dụng, thời gian tối đa là 01 giờ/buổi. |
| 4 | Giấy tờ bạn đọc cần xuất trình khi đến mượn sách tại phòng mượn là gì? | `library-introduction#16`: Quy định tại phòng Mượn mang về nhà sử dụng, xuất trình thẻ và thông tin kiểm tra... | 0.8457 | Có (Relevant - Top 1) | Bạn đọc cần xuất trình Thẻ sinh viên hoặc CMTND/CCCD và đọc đúng mã sinh viên được cấp. |
| 5 | Phòng Đọc thư viện tạm ngừng phục vụ từ ngày nào để sửa chữa nội thất? | `library-notice#0`: Thông báo tạm ngừng phục vụ phòng Đọc từ ngày 04/07/2022 để cải tạo, sửa chữa nội thất... | 0.6022 | Có (Relevant - Top 2) | Phòng Đọc tạm ngừng phục vụ từ ngày 04/07/2022 để sửa chữa nội thất; phòng Mượn hoạt động bình thường. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua phần demo của nhóm, tôi học được rằng cấu trúc tài liệu quyết định tính hiệu quả của chiến lược chunking. Chiến lược `HeadingSectionChunker` của bạn Thái Anh giữ trọn vẹn từng điều khoản quy định mà không bị cắt rời ý, trong khi chiến lược `RecursiveChunker` của tôi kiểm soát kích thước chunk rất mượt mà đối với các tài liệu dài. Kết hợp cả hai (chia theo Heading trước, đoạn nào quá dài thì đệ quy) sẽ tạo ra chiến lược Hybrid tối ưu nhất.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |

