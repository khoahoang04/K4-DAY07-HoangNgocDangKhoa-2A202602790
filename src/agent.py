from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy thông tin phù hợp vì cơ sở tri thức hiện đang rỗng."

        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức để trả lời câu hỏi."

        context_blocks = []
        for i, r in enumerate(results, start=1):
            source = r.get("metadata", {}).get(
                "source", r.get("metadata", {}).get("doc_id", r.get("id", "unknown"))
            )
            context_blocks.append(f"[{i}] (Nguồn: {source}):\n{r['content']}")

        context_str = "\n\n".join(context_blocks)

        prompt = (
            "Bạn là trợ lý AI trả lời câu hỏi dựa trên ngữ cảnh được cung cấp bên dưới.\n"
            "Quy tắc bắt buộc:\n"
            "1. Chỉ sử dụng thông tin có trong phần Ngữ cảnh để trả lời. Tuyệt đối không tự suy đoán hoặc bịa đặt thông tin.\n"
            "2. Khi trả lời, hãy trích dẫn rõ số thứ tự nguồn [1], [2],... tương ứng với đoạn ngữ cảnh đã dùng.\n"
            "3. Nếu ngữ cảnh không có đủ thông tin để trả lời câu hỏi, hãy nói rõ là không tìm thấy thông tin trong tài liệu.\n\n"
            f"--- NGỮ CẢNH ---\n{context_str}\n\n"
            f"--- CÂU HỎI ---\n{question}\n\n"
            "--- CÂU TRẢ LỜI ---"
        )

        return self.llm_fn(prompt)

