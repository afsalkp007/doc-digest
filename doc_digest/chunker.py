"""Hierarchical document section chunker with markdown header and paragraph awareness."""

import re
from typing import List
from doc_digest.models import DocumentSection


class DocumentChunker:
    """Splits long documents into semantic, token-bounded sections for parallel Map processing."""

    def __init__(self, max_words: int = 350, overlap_words: int = 30):
        self.max_words = max_words
        self.overlap_words = overlap_words

    def chunk(self, text: str, default_title: str = "Section") -> List[DocumentSection]:
        """Split text into structured DocumentSection objects."""
        if not text or not text.strip():
            return []

        # 1. Try splitting by Markdown headers (# or ## or ###)
        header_pattern = re.compile(r"^(#{1,3}\s+.+)$", re.MULTILINE)
        splits = header_pattern.split(text.strip())

        sections: List[DocumentSection] = []

        if len(splits) > 1:
            # We found markdown headings
            current_title = default_title
            buffer = ""

            for part in splits:
                part = part.strip()
                if not part:
                    continue

                if header_pattern.match(part):
                    # Flush previous section if exists
                    if buffer.strip():
                        self._add_or_subsplit_section(sections, current_title, buffer)
                        buffer = ""
                    # New title (strip the leading # symbols)
                    current_title = re.sub(r"^#{1,3}\s+", "", part).strip()
                else:
                    buffer += part + "\n\n"

            if buffer.strip():
                self._add_or_subsplit_section(sections, current_title, buffer)

        else:
            # No markdown headers found: split by paragraphs with token budget
            paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
            current_chunk_words: List[str] = []
            chunk_idx = 1

            for p in paragraphs:
                p_words = p.split()
                if len(current_chunk_words) + len(p_words) > self.max_words and current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    sections.append(
                        DocumentSection(
                            section_index=len(sections),
                            title=f"{default_title} (Part {chunk_idx})",
                            content=chunk_text,
                            word_count=len(current_chunk_words),
                            token_estimate=int(len(current_chunk_words) * 1.3),
                        )
                    )
                    chunk_idx += 1
                    # Retain overlap words
                    current_chunk_words = current_chunk_words[-self.overlap_words:] + p_words
                else:
                    current_chunk_words.extend(p_words)

            if current_chunk_words:
                chunk_text = " ".join(current_chunk_words)
                sections.append(
                    DocumentSection(
                        section_index=len(sections),
                        title=f"{default_title} (Part {chunk_idx})" if chunk_idx > 1 else default_title,
                        content=chunk_text,
                        word_count=len(current_chunk_words),
                        token_estimate=int(len(current_chunk_words) * 1.3),
                    )
                )

        return sections

    def _add_or_subsplit_section(self, sections: List[DocumentSection], title: str, text: str) -> None:
        words = text.split()
        if len(words) <= self.max_words * 1.2:
            sections.append(
                DocumentSection(
                    section_index=len(sections),
                    title=title,
                    content=text.strip(),
                    word_count=len(words),
                    token_estimate=int(len(words) * 1.3),
                )
            )
        else:
            # Sub-split long section into parts
            sub_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            part_idx = 1
            curr_words: List[str] = []

            for sp in sub_paragraphs:
                sp_words = sp.split()
                if len(curr_words) + len(sp_words) > self.max_words and curr_words:
                    sub_text = " ".join(curr_words)
                    sections.append(
                        DocumentSection(
                            section_index=len(sections),
                            title=f"{title} (Part {part_idx})",
                            content=sub_text,
                            word_count=len(curr_words),
                            token_estimate=int(len(curr_words) * 1.3),
                        )
                    )
                    part_idx += 1
                    curr_words = curr_words[-self.overlap_words:] + sp_words
                else:
                    curr_words.extend(sp_words)

            if curr_words:
                sub_text = " ".join(curr_words)
                sections.append(
                    DocumentSection(
                        section_index=len(sections),
                        title=f"{title} (Part {part_idx})",
                        content=sub_text,
                        word_count=len(curr_words),
                        token_estimate=int(len(curr_words) * 1.3),
                    )
                )
