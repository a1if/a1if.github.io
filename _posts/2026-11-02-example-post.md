---
title: Example post (formatting guide)
date: 2026-11-02
description: A template showing how headings, code, quotes, tables and images look on the blog. It stays unpublished, so it never appears on the live site.
tags:
  - example
published: false
---

This post is a **template**. It's marked as unpublished, so it never shows on the live site. Duplicate it or start a new post, then delete this one when you no longer need it.

## A section heading

Normal paragraphs look like this. You can use **bold**, *italic*, [links](https://a1if.github.io) and `inline code`.

### A smaller heading

- Bullet points work
- Like this

1. So do numbered lists
2. Like this

> A quote or a key takeaway stands out like this.

## Code

```python
import torch

def accuracy(logits: torch.Tensor, labels: torch.Tensor) -> float:
    # Fraction of predictions that match the labels
    return (logits.argmax(dim=-1) == labels).float().mean().item()
```

## Tables

| Model | Metric A | Metric B |
|---|---|---|
| Model one | 0.00 | 0.00 |
| Model two | 0.00 | 0.00 |

## Images

Upload an image in the editor and it's saved under `images/blog/`. It then shows up full width, like any other paragraph.
