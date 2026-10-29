"""Hierarchical document section chunker with markdown header and token budgeting awareness."""

import re
from typing import List
from doc_digest.models import DocumentSection


class DocumentChunker:
    """Splits long documents into semantic, token-bounded sections for parallel Map processing."""

    def __init__(self, max_words: int = 350, overlap_words: int = 30):
        self.max_words = max(max_words, 20)
        self.overlap_words = min(overlap_words, self.max_words // 2)

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
            # No markdown headers found: split by token budget
            words = text.strip().split()
            if len(words) <= self.max_words * 1.2:
                sections.append(
                    DocumentSection(
                        section_index=0,
                        title=default_title,
                        content=text.strip(),
                        word_count=len(words),
                        token_estimate=int(len(words) * 1.3),
                    )
                )
            else:
                step = max(self.max_words - self.overlap_words, 1)
                part_idx = 1
                for start in range(0, len(words), step):
                    chunk_words = words[start:start + self.max_words]
                    if not chunk_words:
                        break
                    chunk_text = " ".join(chunk_words)
                    sections.append(
                        DocumentSection(
                            section_index=len(sections),
                            title=f"{default_title} (Part {part_idx})",
                            content=chunk_text,
                            word_count=len(chunk_words),
                            token_estimate=int(len(chunk_words) * 1.3),
                        )
                    )
                    part_idx += 1
                    if start + self.max_words >= len(words):
                        break

        return sections

    def chunk_document(self, text: str, title: str = "Section") -> List[DocumentSection]:
        """Convenience alias for chunk()."""
        return self.chunk(text, default_title=title)

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
            # Sub-split long section into word-bounded parts with overlap
            step = max(self.max_words - self.overlap_words, 1)
            part_idx = 1
            for start in range(0, len(words), step):
                chunk_words = words[start:start + self.max_words]
                if not chunk_words:
                    break
                sub_text = " ".join(chunk_words)
                sections.append(
                    DocumentSection(
                        section_index=len(sections),
                        title=f"{title} (Part {part_idx})",
                        content=sub_text,
                        word_count=len(chunk_words),
                        token_estimate=int(len(chunk_words) * 1.3),
                    )
                )
                part_idx += 1
                if start + self.max_words >= len(words):
                    break
