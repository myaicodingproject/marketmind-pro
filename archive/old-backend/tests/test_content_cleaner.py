#!/usr/bin/env python3
"""
Test script to verify ContentCleaner functionality
"""

from professional_pdf_generator import ContentCleaner

def test_content_cleaning():
    """Test the content cleaning functionality"""
    cleaner = ContentCleaner()
    
    # Test content with various markdown artifacts and AI messages
    test_content = """
# Executive Summary

> I'll analyze the financial data for you

Invoking 8 subagents in parallel (using tool: kiro_execute)

## Investment Recommendation: **BUY**

The company shows strong fundamentals with the following metrics:

- Revenue growth of 15%
- **Strong** market position
- *Excellent* management team

| Metric | Value | Change |
|--------|-------|--------|
| Revenue | $100B | +15% |
| Profit | $25B | +20% |

```python
# Some code block
revenue = 100
```

References: [1] SEC Filing 10-K

■■■■■■■■■■■■■■■

━━━━━━━━━━━━━━━

192: + 193: Line numbers here

using tool: web_search

> This is another AI message

1. First numbered item
2. Second numbered item
* Bullet item with asterisk

**Bold text** and *italic text* and __alternative bold__ and _alternative italic_

Multiple    spaces    here

Multiple


newlines


here
    """
    
    # Test the structure_section method which includes full formatting
    section_data = {'title': 'Executive Summary', 'content': test_content}
    structured = cleaner.structure_section('executive_summary', section_data)
    
    print("=== ORIGINAL CONTENT ===")
    print(test_content)
    print("\n=== STRUCTURED CONTENT ===")
    print(structured['content'])
    
    cleaned = structured['content']
    
    # Verify cleaning worked
    assert "Invoking" not in cleaned
    assert "using tool:" not in cleaned
    assert "> I'll" not in cleaned  # Specific AI message pattern
    assert "> This is" not in cleaned  # Another AI message pattern
    assert "■■■" not in cleaned
    assert "━━━" not in cleaned
    assert "192: + 193:" not in cleaned
    assert "References:" not in cleaned
    assert "```" not in cleaned
    assert "|" not in cleaned or cleaned.count("|") < 3  # Table formatting removed
    assert "<strong>" in cleaned  # Bold converted
    assert "<em>" in cleaned  # Italic converted
    assert "<ul>" in cleaned or "<li>" in cleaned  # Lists converted
    
    print("\n✅ All content cleaning tests passed!")

if __name__ == "__main__":
    test_content_cleaning()