# HiMCM 2026 Problem B — Typst draft (Team 18388, v9)

## Build

```text
cd D:\Conditioner\paper
python compile_v8.py
```

Output: `18388_v9.pdf` (Times New Roman required).

## Regenerate numbers / figures

```text
cd D:\Conditioner
python -m model_v8.run_all_v9
```

## Polish English (DeepSeek)

```text
cd D:\Conditioner\paper
python scripts/polish_prose_deepseek.py
```

Uses `DEEPSEEK_API_KEY` if set. Keeps Typst markup and numeric claims.
