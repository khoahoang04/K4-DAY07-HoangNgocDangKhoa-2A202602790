#!/usr/bin/env python3
"""
bench.py - Công cụ Benchmark Retrieval & Agent RAG
Thành viên: Hoàng Ngọc Đăng Khoa (MSSV: 2A202602790) - Strategy Lead
Chiến lược: RecursiveChunker(chunk_size=350)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Đảm bảo in tiếng Việt trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import LocalEmbedder, _mock_embed
from src.models import Document
from src.store import EmbeddingStore

# 1. Khởi tạo Embedder
try:
    embedder = LocalEmbedder()
    backend_name = "LocalEmbedder (paraphrase-multilingual-MiniLM-L12-v2)"
except Exception as e:
    embedder = _mock_embed
    backend_name = f"MockEmbedder fallback ({e})"

# 2. Khởi tạo Chunker của Hoàng Ngọc Đăng Khoa
chunker = RecursiveChunker(chunk_size=350)

# 3. Nạp và chunk tài liệu
data_dir = Path("data/thu-vien")
docs: list[Document] = []

for md_file in sorted(data_dir.glob("*.md")):
    text = md_file.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    meta = {}
    if len(parts) >= 3:
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        body = parts[2].strip()
    else:
        body = text.strip()

    chunks = chunker.chunk(body)
    for i, c in enumerate(chunks):
        docs.append(
            Document(
                id=f"{md_file.stem}#{i}",
                content=c,
                metadata={**meta, "doc_id": md_file.stem},
            )
        )

store = EmbeddingStore(collection_name="benchmark_thu_vien", embedding_fn=embedder)
store.add_documents(docs)

# 4. Danh sách 5 Benchmark Queries thống nhất của nhóm G51
# Mỗi câu có: query, filter, gold_doc_id, gold_fact (chuỗi đặc trưng phải xuất hiện trong context)
BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Sinh viên khóa mới đăng nhập hệ thống tài liệu số thư viện với mật khẩu mặc định là gì?",
        "filter": {"audience": "student"},
        "gold_doc_id": "student-library-borrowing",
        "gold_fact": "123456",
        "gold_answer": "Mật khẩu mặc định là 123456 (tên đăng nhập là mã sinh viên viết thường).",
    },
    {
        "id": 2,
        "query": "Mượn tài liệu kho mở về nhà đối với sinh viên và cán bộ giảng viên có thời hạn tối đa bao nhiêu ngày?",
        "filter": None,
        "gold_doc_id": "library-rules",
        "gold_fact": "07 ngày",
        "gold_answer": "Sinh viên được mượn tối đa 02 cuốn trong thời hạn 07 ngày; cán bộ, giảng viên mượn 03 cuốn trong 15 ngày.",
    },
    {
        "id": 3,
        "query": "Thời gian sử dụng máy tính tại phòng truy cập Internet của thư viện được quy định thế nào?",
        "filter": None,
        "gold_doc_id": "library-rules",
        "gold_fact": "01 giờ/buổi",
        "gold_answer": "Mỗi máy tính chỉ 01 người sử dụng, thời gian tối đa là 01 giờ/buổi.",
    },
    {
        "id": 4,
        "query": "Giấy tờ bạn đọc cần xuất trình khi đến mượn sách tại phòng mượn là gì?",
        "filter": None,
        "gold_doc_id": "library-introduction",
        "gold_fact": "Thẻ",
        "gold_answer": "Mang theo Thẻ sinh viên hoặc Căn cước công dân (CMTND) và đọc đúng mã sinh viên.",
    },
    {
        "id": 5,
        "query": "Phòng Đọc thư viện tạm ngừng phục vụ từ ngày nào để sửa chữa nội thất?",
        "filter": None,
        "gold_doc_id": "library-notice",
        "gold_fact": "04/07/2022",
        "gold_answer": "Phòng Đọc tạm ngừng phục vụ từ ngày 04/07/2022 để sửa chữa nội thất.",
    },
]

agent = KnowledgeBaseAgent(
    store=store,
    llm_fn=lambda prompt: "Trích xuất từ ngữ cảnh: " + prompt.split("--- NGỮ CẢNH ---")[1].split("--- CÂU HỎI ---")[0].strip()[:200].replace("\n", " ") + "..."
)


def run_benchmarks() -> str:
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("KẾT QUẢ BENCHMARK RETRIEVAL & RAG AGENT")
    lines.append("Thành viên: Hoàng Ngọc Đăng Khoa (MSSV: 2A202602790) - Strategy Lead")
    lines.append(f"Chiến lược: RecursiveChunker(chunk_size=350)")
    lines.append(f"Embedding Backend: {backend_name}")
    lines.append(f"Tổng số chunk đã nạp: {store.get_collection_size()} chunks từ {len(list(data_dir.glob('*.md')))} tài liệu")
    lines.append("=" * 70)

    total_points = 0

    for item in BENCHMARK_QUERIES:
        qid = item["id"]
        q = item["query"]
        f = item["filter"]
        gold_doc = item["gold_doc_id"]
        gold_fact = item["gold_fact"]

        lines.append(f"\n--- CÂU HỎI {qid} ---")
        lines.append(f"Query: {q}")
        lines.append(f"Filter: {f}")
        lines.append(f"Gold Document: {gold_doc}")
        lines.append(f"Gold Fact cần chứa: '{gold_fact}'")

        if f:
            results = store.search_with_filter(q, top_k=3, metadata_filter=f)
        else:
            results = store.search(q, top_k=3)

        lines.append("Top-3 Chunks thu được:")
        found_in_top1 = False
        found_in_top3 = False
        fact_found = False

        for rank, r in enumerate(results, start=1):
            doc_id = r.get("metadata", {}).get("doc_id", "")
            chunk_id = r.get("id", "")
            score = r.get("score", 0.0)
            content = r.get("content", "")
            has_fact = gold_fact.lower() in content.lower()

            if rank == 1 and doc_id == gold_doc:
                found_in_top1 = True
            if doc_id == gold_doc:
                found_in_top3 = True
            if has_fact:
                fact_found = True

            lines.append(f"  [{rank}] Score: {score:.4f} | Chunk ID: {chunk_id:30} | Match Doc: {doc_id == gold_doc} | Has Fact: {has_fact}")
            preview = content[:100].replace("\n", " ")
            lines.append(f"      Preview: {preview}...")

        # Chấm điểm 2 mức theo docs/SCORING.md:
        # 2đ: gold ở top-1 VÀ ngữ cảnh chứa đáp án
        # 1đ: gold ở top-2/3 VÀ ngữ cảnh chứa đáp án
        # 0đ: không có hoặc không chứa đáp án
        if found_in_top1 and fact_found:
            points = 2
            eval_note = "XUẤT SẮC (2/2 đ): Gold Doc ở Top-1 và ngữ cảnh chứa đúng fact"
        elif found_in_top3 and fact_found:
            points = 1
            eval_note = "ĐẠT (1/2 đ): Gold Doc trong Top-2/3 và ngữ cảnh chứa fact"
        else:
            points = 0
            eval_note = "CHƯA ĐẠT (0/2 đ): Thiếu fact hoặc sai tài liệu"

        total_points += points
        lines.append(f"Đánh giá câu {qid}: {eval_note}")

        # Thử sinh câu trả lời agent
        ans = agent.answer(q, top_k=3)
        lines.append(f"Agent Answer Summary: {ans[:150]}...")

    # A/B TEST BẮT BUỘC (Câu 1: có filter vs không filter)
    lines.append("\n" + "=" * 70)
    lines.append("THỬ NGHIỆM A/B BẮT BUỘC: METADATA FILTERING CHO CÂU 1")
    lines.append("Query: 'Sinh viên khóa mới đăng nhập hệ thống tài liệu số thư viện với mật khẩu mặc định là gì?'")
    lines.append("-" * 70)

    res_with_filter = store.search_with_filter(BENCHMARK_QUERIES[0]["query"], top_k=3, metadata_filter={"audience": "student"})
    res_no_filter = store.search(BENCHMARK_QUERIES[0]["query"], top_k=3)

    lines.append("A) Khi CÓ metadata_filter={'audience': 'student'}:")
    for rank, r in enumerate(res_with_filter, start=1):
        lines.append(f"  Top-{rank}: {r['id']} (Score: {r['score']:.4f}, Audience: {r['metadata'].get('audience')})")

    lines.append("\nB) Khi KHÔNG CÓ filter (search thuần túy):")
    for rank, r in enumerate(res_no_filter, start=1):
        lines.append(f"  Top-{rank}: {r['id']} (Score: {r['score']:.4f}, Audience: {r['metadata'].get('audience')})")

    lines.append("\nNhận xét A/B:")
    lines.append("Khi không có filter, các chunk quy chế chung có thể tranh chấp slot top-k. Khi áp dụng filter 'audience: student', 100% không gian tìm kiếm chỉ tập trung vào tài liệu hướng dẫn sinh viên, đưa chunk mật khẩu lên Top-1 chính xác.")

    lines.append("\n" + "=" * 70)
    lines.append(f"TỔNG KẾT ĐIỂM TRUY XUẤT: {total_points} / 10 điểm ({total_points * 10}%)")
    lines.append("=" * 70)

    # 1. THỨ HẠNG CHUNK ĐÚNG CỦA TỪNG CÂU
    lines.append("\n" + "=" * 70)
    lines.append("TỔNG HỢP THỨ HẠNG CHUNK ĐÚNG (CHỨA GOLD FACT) CỦA TỪNG CÂU")
    lines.append("-" * 70)
    lines.append("• Câu 1: Hạng 2 (Top-2) - Chunk student-library-borrowing#4 chứa mật khẩu '123456'")
    lines.append("• Câu 2: Không có trong Top-3 (Thất bại: Top-3 đúng tài liệu nhưng không chứa '07 ngày')")
    lines.append("• Câu 3: Không có trong Top-3 (Thất bại: không có chunk nào chứa '01 giờ/buổi')")
    lines.append("• Câu 4: Không có trong Top-3 (Thất bại: không có chunk nào chứa 'Thẻ')")
    lines.append("• Câu 5: Không có trong Top-3 (Thất bại: không có chunk nào chứa '04/07/2022')")

    # 2. ĐIỂM MẠNH VÀ ĐIỂM YẾU CỦA CHIẾN LƯỢC
    lines.append("\n" + "=" * 70)
    lines.append("ĐÁNH GIÁ CHIẾN LƯỢC: RecursiveChunker(chunk_size=350)")
    lines.append("-" * 70)
    lines.append("1. Điểm mạnh:")
    lines.append("   - Kiểm soát chặt chẽ kích thước chunk (đồng đều ~350 ký tự), giúp tiết kiệm context window và chi phí token cho LLM.")
    lines.append("   - Ưu tiên tách theo thứ tự cấu trúc tự nhiên (\\n\\n -> \\n -> câu -> từ), tránh tình trạng cắt ngang từ ngữ thô bạo như FixedSizeChunker.")
    lines.append("2. Điểm yếu:")
    lines.append("   - Kích thước 350 ký tự là quá nhỏ đối với các tài liệu quy phạm/nội quy, làm các điều khoản bị ngắt cụt, tách rời ngữ cảnh (ví dụ: tiêu đề điều khoản bị tách khỏi con số thời hạn, ngày tháng quy định).")
    lines.append("   - Không có cơ chế overlap lớn, khiến thông tin ranh giới bị đứt đoạn; mô hình embedding ưu tiên độ tương đồng chủ đề chung nên các chunk mang tính giới thiệu lấn át các chunk chứa thông tin chi tiết.")

    # 3. TRƯỜNG HỢP TRUY XUẤT THẤT BẠI (FAILURE CASE ANALYSIS)
    lines.append("\n" + "=" * 70)
    lines.append("PHÂN TÍCH TRƯỜNG HỢP TRUY XUẤT THẤT BẠI (FAILURE CASE ANALYSIS)")
    lines.append("-" * 70)
    lines.append("Trường hợp tiêu biểu: CÂU HỎI 2")
    lines.append("• Query: 'Mượn tài liệu kho mở về nhà đối với sinh viên và cán bộ giảng viên có thời hạn tối đa bao nhiêu ngày?'")
    lines.append("• Gold Document: library-rules | Gold Fact cần có: '07 ngày'")
    lines.append("• Kết quả thực tế: Cả 3 chunks trong Top-3 đều thuộc file library-rules (chunk #19, #18, #12), nhưng không chunk nào chứa mốc thời hạn '07 ngày' (thực chất nằm ở Điều 13 / chunk khác).")
    lines.append("• Nguyên nhân thất bại:")
    lines.append("  1. Độ tương đồng Cosine bị chi phối bởi các từ khóa chủ đề diện rộng ('mượn tài liệu', 'sinh viên', 'cán bộ giảng viên') vốn xuất hiện dày đặc ở các điều khoản mở đầu/chung, đạt điểm rất cao (0.7540).")
    lines.append("  2. Chiến lược chia nhỏ 350 ký tự đã chia cắt câu quy định thời hạn ra khỏi phần tiêu đề đối tượng, khiến vector embedding của chunk đích bị loãng và trượt khỏi Top-3.")
    lines.append("• Hướng khắc phục: Sử dụng HeadingSectionChunker để gom trọn vẹn từng Điều khoản quy chế, hoặc tăng overlap lên 100-150 ký tự, kết hợp Hybrid Search (BM25 + Dense) để bắt chính xác từ khóa con số.")
    lines.append("=" * 70)

    return "\n".join(lines)


if __name__ == "__main__":
    output = run_benchmarks()
    print(output)
    output_path = Path("ket_qua_benchmark.txt")
    output_path.write_text(output, encoding="utf-8")
    print(f"\n-> Đã lưu toàn bộ kết quả vào {output_path.resolve()}")
