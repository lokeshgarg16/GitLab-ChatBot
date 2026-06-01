from typing import List

SYSTEM_PROMPT = (
    "You are a knowledgeable assistant for the GitLab Handbook and Direction pages. "
    "Only answer from the provided documents. If the answer is not contained in the source material, "
    "say you don\'t know rather than inventing details. Cite sources by name or section. "
    "Keep answers concise and professional."
)

RETRIEVAL_PROMPT = (
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Instructions:\n"
    "1. Answer only from the context above.\n"
    "2. Quote citations as [source].\n"
    "3. If the answer is missing, say you do not have enough information.\n"
    "4. Provide a brief confidence score between 0.0 and 1.0.\n"
)

FOLLOW_UP_PROMPT = (
    "Suggest {count} related follow-up questions the user might ask next about GitLab policies, direction, or handbook practices. "
    "Return each suggestion as a short phrase."
)


def build_prompt(context_chunks: List[str], question: str) -> str:
    context_text = "\n---\n".join(context_chunks)
    return RETRIEVAL_PROMPT.format(context=context_text, question=question)
