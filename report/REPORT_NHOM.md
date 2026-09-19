# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G51  
**Lớp:** K4-L3A  
**Thành viên:**  
1. Đoàn Quang Minh (R1 · Data Lead)  
2. Ngọ Doãn Ngọc (Code Lead)  
3. Hoàng Ngọc Đăng Khoa (Strategy Lead)  
4. Nguyễn Thái Anh (R2 & Demo Lead)  
**Ngày:** 19/09/2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Hệ thống Quy định & Dịch vụ Thông tin Thư viện Đại học (Học viện Công nghệ Bưu chính Viễn thông - PTIT)

**Tại sao nhóm chọn chủ đề này?**
> Thư viện là trung tâm dịch vụ học vụ thiết yếu hàng ngày của sinh viên và cán bộ giảng viên, bao gồm các quy định chặt chẽ về mượn - trả tài liệu in, hệ thống thư viện số (Dspace) và cổng tra cứu trực tuyến OPAC. Nguồn dữ liệu hoàn toàn công khai, minh bạch, có cấu trúc điều khoản phân cấp rõ ràng và có sự phân hóa tự nhiên giữa các đối tượng độc giả (`audience`: `student` vs `all`), rất lý tưởng để thử nghiệm truy xuất thông tin và lọc metadata.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Nội quy thư viện PTIT | https://lib.ptit.edu.vn/noi-quy-thu-vien/ | 2026-09-19 / not-stated | 3,320 | `audience: all`, `category: regulation`, `department: library` |
| 2 | Giới thiệu Trung tâm Thông tin Thư viện PTIT | https://lib.ptit.edu.vn/gioi-thieu/ | 2026-09-19 / not-stated | 2,350 | `audience: all`, `category: service`, `department: library` |
| 3 | Thông báo mượn tài liệu in và số cho sinh viên | https://lib.ptit.edu.vn/thong-bao-ve-viec-muon-tai-lieu-in-va-tai-lieu-so-cho-sinh-vien-khoa-d19-nam-hoc-2019-2020/ | 2026-09-19 / not-stated | 1,420 | `audience: student`, `category: borrowing`, `department: library` |
| 4 | Thông báo về phục vụ bạn đọc tại thư viện | https://lib.ptit.edu.vn/thong-bao-ve-phuc-vu-ban-doc-tai-thu-vien-tu-2122022/ | 2026-09-19 / not-stated | 1,280 | `audience: all`, `category: service`, `department: library` |
| 5 | Thông báo hoạt động thư viện | https://lib.ptit.edu.vn/thong-bao-2/ | 2026-09-19 / not-stated | 1,310 | `audience: all`, `category: notice`, `department: library` |
| 6 | Cổng thông tin thư viện OPAC PTIT | https://lib.ptit.edu.vn/opac/ | 2026-09-19 / not-stated | 1,590 | `audience: student`, `category: search-service`, `department: library` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `"library-rules"` | Định danh duy nhất của tài liệu để truy vết nguồn và phục vụ xóa/cập nhật. |
| `title` | `str` | `"Nội quy thư viện PTIT"` | Cung cấp ngữ cảnh tiêu đề phục vụ hiển thị kết quả cho người dùng. |
| `source_url` | `str` | `"https://lib.ptit.edu.vn/noi-quy-thu-vien/"` | Nguồn gốc kiểm chứng, cho phép người dùng click xem văn bản gốc. |
| `retrieved_at` | `str` | `"2026-09-19"` | Đánh giá độ mới của thông tin trong cơ sở tri thức. |
| `document_version` | `str` | `"not-stated"` | Quản lý phiên bản quy chế khi nhà trường có điều chỉnh mới. |
| `audience` | `str` | `"student"` / `"all"` | **Trường cốt lõi để lọc metadata:** Phân tách chính sách riêng cho sinh viên với quy định chung cho cán bộ/giảng viên. |
| `department` | `str` | `"library"` | Lọc phạm vi đơn vị ban hành khi tích hợp nhiều phòng ban trường học. |
| `category` | `str` | `"regulation"`, `"borrowing"` | Gom cụm chủ đề tìm kiếm theo tính chất (nội quy, mượn sách, thông báo). |
| `language` | `str` | `"vi"` | Định tuyến ngôn ngữ xử lý văn bản tiếng Việt. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` với `chunk_size=300`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `library-rules.md` | FixedSizeChunker (`fixed_size`) | 18 | 298.7 ký tự | Kém: Cắt ngang giữa các điều khoản, tách rời số lượng sách với thời hạn mượn. |
| `library-rules.md` | SentenceChunker (`by_sentences`) | 16 | 312.4 ký tự | Khá: Giữ được câu hoàn chỉnh nhưng các điều khoản có nhiều câu con bị phân mảnh. |
| `library-rules.md` | RecursiveChunker (`recursive`) | 22 | 227.7 ký tự | Tốt: Tách tự nhiên theo đoạn `\n\n` và dấu câu, các khối điều khoản tương đối nguyên vẹn. |
| `student-library-borrowing.md` | FixedSizeChunker (`fixed_size`) | 6 | 286.0 ký tự | Trung bình: Cắt đều độ dài nhưng ngắt giữa chừng các dòng hướng dẫn tài khoản. |
| `student-library-borrowing.md` | SentenceChunker (`by_sentences`) | 2 | 806.5 ký tự | Kém: Bị phình to (806 ký tự) do văn bản có nhiều dòng danh sách thiếu dấu chấm câu. |
| `student-library-borrowing.md` | RecursiveChunker (`recursive`) | 8 | 200.5 ký tự | Rất tốt: Cắt rất đẹp theo dòng xuống dòng `\n` của từng mục hướng dẫn. |
| `library-introduction.md` | FixedSizeChunker (`fixed_size`) | 10 | 280.2 ký tự | Khá: Tách đều đặn nhưng ngắt đôi danh sách máy tính và diện tích các phòng. |
| `library-introduction.md` | SentenceChunker (`by_sentences`) | 8 | 324.6 ký tự | Khá: Câu văn rõ ràng nhưng bảng vị trí phòng ốc bị gộp chung. |
| `library-introduction.md` | RecursiveChunker (`recursive`) | 12 | 217.2 ký tự | Tốt: Giữ trọn từng khối thông tin lịch sử, chức năng và phòng ban. |

#### Chiến lược của từng thành viên

**Thành viên 1 — Đoàn Quang Minh (MSSV: 2A202602711 · R1 · Data Lead)**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=500`, `overlap=50` và thử nghiệm `overlap=100`)
- **Mô tả & lý do chọn cho chủ đề này:** Dựa trên phân tích toán học chunking ($ceil((10000 - 50) / (500 - 50)) = 23$ chunk). Minh chọn FixedSize làm đường cơ sở để đo đạc kích thước vector đồng đều, đồng thời kiểm chứng việc tăng `overlap` lên 100 ký tự (sinh 25 chunks) giúp giảm thiểu tối đa hiện tượng đứt gãy ngữ cảnh khi câu quy định học vụ nằm vắt ngang qua ranh giới cắt.

**Thành viên 2 — Ngọ Doãn Ngọc (MSSV: 2A202602635 · Code Lead)**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=3`) kết hợp thử nghiệm `HeadingChunker`
- **Mô tả & lý do chọn cho chủ đề này:** Sử dụng biểu thức chính quy Lookbehind `r"(?<=[.!?])(?:\s+|\n+)"` để tách câu trọn vẹn mà không nuốt dấu chấm câu. Ngọc nhận xét: chiến lược tách câu giữ được cấu trúc ngữ pháp tự nhiên, nhưng khi gặp văn bản quy định có nhiều danh sách gạch đầu dòng không có dấu chấm thì chunk dễ bị phình to (ví dụ tài liệu mượn sách lên tới 806 ký tự), do đó việc chuyển sang cắt theo Heading giúp ổn định kích thước chunk (~240 ký tự).

**Thành viên 3 — Hoàng Ngọc Đăng Khoa (MSSV: 2A202602790 · Strategy Lead)**
- **Loại chiến lược:** RecursiveChunker (danh sách separators `["\n\n", "\n", ". ", " "]`, `chunk_size=350`)
- **Mô tả & lý do chọn cho chủ đề này:** Cắt văn bản theo thuật toán 2 chiều: đệ quy xuống sâu theo mức độ ưu tiên của dấu phân cách và gom lên (merge) các mảnh liền kề chừng nào còn $\le \text{chunk\_size}$. Khoa chọn chiến lược này vì văn bản thư viện có cấu trúc đa tầng (đoạn văn, dòng đơn, điều khoản con), giúp thích ứng linh hoạt mà không sinh ra các mẩu vụn 5–10 ký tự.

**Thành viên 4 — Nguyễn Thái Anh (MSSV: 2A202602810 · R2 & Demo Lead — Biến thể L3A bắt buộc)**
- **Loại chiến lược:** Custom `HeadingSectionChunker` (Tách văn bản theo các tiêu đề `#`, `##` và điều khoản quy định)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy định đại học luôn được tổ chức phân cấp chặt chẽ theo các mục và Điều khoản (`Điều 1`, `Điều 13`, `Điều 22`). Chiến lược này giữ trọn vẹn toàn bộ một điều khoản trong cùng một chunk duy nhất, đảm bảo tính toàn vẹn ngữ nghĩa 100%.
- **Code snippet:**
```python
import re

class HeadingSectionChunker:
    """Tách văn bản quy định đại học theo các tiêu đề Markdown và Điều khoản."""
    def chunk(self, text: str) -> list[str]:
        # Bỏ khối metadata frontmatter nếu có
        parts = text.split("---")
        body = "---".join(parts[2:]).strip() if len(parts) >= 3 else text.strip()
        # Cắt theo các tiêu đề Markdown (#, ##, ###)
        pattern = r'(?m)(?=^#{1,3}\s+)'
        sections = re.split(pattern, body)
        return [s.strip() for s in sections if s.strip()]
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Đoàn Quang Minh | FixedSize (500/50) | 7.5 / 10 | Đơn giản, kích thước vector đồng đều, overlap bảo vệ ranh giới cắt. | Cắt cơ học theo số ký tự, dễ ngắt ngang điều khoản quy định. |
| Ngọ Doãn Ngọc | Sentence / Heading (3 câu) | 9.0 / 10 (4/5 câu Top-3) | Câu văn nguyên vẹn, bảo toàn ngữ cảnh tiêu đề tốt. | Bị phình to khi gặp văn bản gạch đầu dòng thiếu dấu chấm câu. |
| Hoàng Ngọc Đăng Khoa | Recursive (350) | 8.5 / 10 | Thích ứng rất tốt với văn bản nhiều cấp độ (đoạn, dòng, câu), không sinh chunk vụn. | Cần tinh chỉnh bộ separators cho phù hợp từng văn bản. |
| Nguyễn Thái Anh | HeadingSection (Custom) | 10.0 / 10 (5/5 câu Top-3) | Giữ 100% ngữ cảnh pháp lý của từng điều khoản, độ chính xác câu trả lời cao nhất. | Độ dài các chunk không đều nhau tùy thuộc vào độ dài từng điều khoản. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **`HeadingSectionChunker`** (kết hợp với `RecursiveChunker` cho các mục có nội dung quá dài) là chiến lược tối ưu nhất cho văn bản quy chế đại học. Cả 4 thành viên đều thống nhất rằng: các câu hỏi tra cứu học vụ của sinh viên luôn gắn liền với một đơn vị quy định trọn vẹn (ví dụ: một Điều khoản chứa đồng thời đối tượng, số lượng mượn, thời hạn và chế tài); việc cắt theo heading giúp bảo toàn toàn bộ ngữ cảnh cần thiết để LLM tổng hợp câu trả lời chính xác mà không bị phân mảnh.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 *(filter)* | Sinh viên khóa mới đăng nhập hệ thống tài liệu số thư viện với mật khẩu mặc định là gì? | Mật khẩu mặc định là 123456 (tên đăng nhập là mã sinh viên viết thường, ví dụ: b17dccn123). | `student-library-borrowing.md` (Mục 2: Hướng dẫn truy cập tài liệu số) |
| 2 | Mượn tài liệu kho mở về nhà đối với sinh viên và cán bộ giảng viên có thời hạn tối đa bao nhiêu ngày? | Sinh viên được mượn tối đa 02 cuốn trong thời hạn 07 ngày; cán bộ, giảng viên được mượn tối đa 03 cuốn trong thời hạn 15 ngày. | `library-rules.md` (Điều 13: Quy định mượn tài liệu kho mở về nhà) |
| 3 | Thời gian sử dụng máy tính tại phòng truy cập Internet của thư viện được quy định thế nào? | Mỗi máy tính chỉ 01 người sử dụng, thời gian tối đa là 01 giờ/buổi. | `library-rules.md` (Điều 15: Nội quy phòng truy cập Internet) |
| 4 | Giấy tờ bạn đọc cần xuất trình khi đến mượn sách tại phòng mượn là gì? | Mang theo Thẻ sinh viên hoặc Căn cước công dân (CMTND) và đọc đúng mã sinh viên được cấp. | `library-reader-service.md` (Mục 3: Quy định phục vụ tại phòng mượn) |
| 5 | Phòng Đọc thư viện tạm ngừng phục vụ từ ngày nào để sửa chữa nội thất? | Phòng Đọc tạm ngừng phục vụ từ ngày 04/07/2022 để sửa chữa nội thất; Phòng Mượn vẫn mở cửa bình thường. | `library-notice.md` (Nội dung thông báo) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mật khẩu mặc định thư viện số cho sinh viên khóa mới | `HeadingSection` + Filter `audience: student` | Có (Top 1) | Lọc metadata giúp loại bỏ hoàn toàn các tài liệu chung, đưa thẳng thông tin mật khẩu lên Top 1. (2/2 đ) |
| 2 | Thời hạn mượn tài liệu kho mở về nhà | `HeadingSection` | Có (Top 1) | Trích xuất trọn vẹn Điều 13, LLM phân biệt rành mạch sinh viên 7 ngày vs giảng viên 15 ngày. (2/2 đ) |
| 3 | Thời gian dùng phòng Internet | `RecursiveChunker` / `HeadingSection` | Có (Top 1) | Điều 15 được truy xuất chính xác với quy định 01 giờ/buổi. (2/2 đ) |
| 4 | Giấy tờ xuất trình tại phòng mượn | `HeadingSection` / `SentenceChunker` | Có (Top 1) | Trích xuất đúng yêu cầu thẻ SV / CMTND tại phòng mượn. (2/2 đ) |
| 5 | Thời gian tạm ngừng phòng đọc sửa chữa | `RecursiveChunker` | Có (Top 1) | Thông báo ngày 04/07/2022 được trích xuất hoàn hảo. (2/2 đ) |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Lọc bằng metadata cực kỳ hữu ích, đặc biệt ở Câu hỏi 1.** Nhóm đã chạy thử nghiệm A/B bắt buộc trên câu hỏi 1:
> - **Khi CÓ `metadata_filter={"audience": "student"}`:** Top-1 là `student-library-borrowing#0` (0.6575) và Top-2 là `student-library-borrowing#4` (0.5501) — **chứa đúng mật khẩu mặc định `123456`**.
> - **Khi KHÔNG CÓ filter (search thuần túy):** Top-1 là `student-library-borrowing#0` (0.6575), nhưng Top-2 và Top-3 bị chiếm bởi các chunk nội quy chung `library-rules#9` (0.5745) và `library-rules#8` (0.5557). Chunk chứa mật khẩu bị đẩy văng khỏi Top-3, khiến Agent không thể trả lời được mật khẩu!
> Điều này chứng minh: nếu không có metadata filter, tài liệu chung sẽ chiếm hết các slot top-k, làm hỏng câu trả lời.

### Phân tích trường hợp thất bại (Failure Case Analysis)

Nhóm phân tích chi tiết một trường hợp thất bại thực tế (failure case) phát hiện được qua `bench.py` khi chạy với `RecursiveChunker`:

1. **Câu hỏi bị hỏng:** Câu 2 — *"Mượn tài liệu kho mở về nhà đối với sinh viên và cán bộ giảng viên có thời hạn tối đa bao nhiêu ngày?"* (Gold Doc: `library-rules.md`, đáp án cần chứa: `"07 ngày"`, `"15 ngày"`).
2. **Nguyên nhân (Vì sao hỏng):**
   - **Đúng tài liệu nhưng sai section (chấm mức 1 vs mức 2):** Cả 3 chunk trong Top-3 đều thuộc đúng tài liệu gold `library-rules` (gồm `#19`, `#18`, `#12`). Nếu chỉ chấm ngây thơ theo `doc_id` thì câu này đạt điểm tối đa. Nhưng khi chấm theo chuỗi đặc trưng nội dung (fact check), không có chunk nào chứa con số `"07 ngày"` hay `"15 ngày"` (vốn nằm ở Điều 13 cụ thể).
   - **Cosine similarity thiên về độ tương đồng chủ đề, không đo mật độ thông tin:** Các chunk mở đầu điều khoản lặp lại nhiều từ khóa `"mượn tài liệu"`, `"sinh viên"`, `"cán bộ giảng viên"` nên đạt điểm cosine rất cao (0.7540), đánh bại chunk chứa con số cụ thể.
   - **Thiếu overlap giữa các section:** Khi chunk cắt cứng theo ranh giới, điều khoản bị chia tách và con số thời hạn chỉ xuất hiện ở một chunk duy nhất, mất đi cơ hội lọt vào top-3.
3. **Đề xuất sửa đổi:**
   - **Chuyển sang `HeadingSectionChunker`:** Gom toàn bộ một Điều khoản quy chế vào một chunk nguyên vẹn, đảm bảo đối tượng và số ngày mượn luôn đi liền nhau.
   - **Tăng Overlap (100–150 ký tự):** Nếu dùng fixed/recursive chunker, bắt buộc tăng overlap để các con số quy định không bị tách rời khỏi câu chủ đề.
   - **Áp dụng Hybrid Search (BM25 + Dense Vector):** Tìm kiếm từ khóa chính xác sẽ tăng trọng số cho các từ vựng con số cụ thể (*"thời hạn"*, *"07 ngày"*), kéo chunk có đáp án lên Top-1.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Cấu trúc văn bản quyết định chiến lược chia nhỏ:** Với các tài liệu có tính quy phạm/pháp lý cao (nội quy, học vụ), chiến lược chia nhỏ theo tiêu đề mục (`HeadingSectionChunker`) vượt trội hoàn toàn so với Fixed-size vì không làm rách rời các điều kiện, số lượng và thời hạn.
> 2. **Sức mạnh của Metadata Filtering:** Metadata không chỉ để lưu trữ mà là một bộ lọc thu hẹp không gian vector trước khi tính độ tương tự, giải quyết triệt để bài toán mâu thuẫn chính sách giữa các nhóm đối tượng (`student` vs `faculty`).
> 3. **Hạn chế của Mock Embedder:** Mock embedder băm MD5 chỉ phục vụ kiểm thử cấu trúc pipeline; trong thực tế chất lượng RAG phụ thuộc 80% vào chất lượng không gian vector ngữ nghĩa của mô hình embedding.

**Bài học rút ra khi so sánh trong nhóm:**
> Khi thử nghiệm trên cùng một tập tài liệu, việc thay đổi chiến lược chunking tạo ra sự khác biệt rất lớn về ngữ cảnh đưa vào prompt. Chunk quá nhỏ gây mất thông tin (cụt ý), còn chunk quá lớn hoặc phình to làm loãng thông tin và tăng chi phí token của LLM.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ áp dụng chiến lược **Hybrid Chunking** (kết hợp cấp độ cha - con): chia các mục lớn theo Heading (Parent Chunk) để lưu trữ toàn bộ ngữ cảnh, sau đó chia nhỏ thành các đoạn 100–200 ký tự (Child Chunk) để nhúng vector; khi tìm kiếm sẽ match ở child chunk nhưng trả về parent chunk cho LLM sinh câu trả lời.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
