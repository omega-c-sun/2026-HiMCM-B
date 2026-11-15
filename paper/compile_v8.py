from pathlib import Path
import typst

root = Path(__file__).resolve().parent
out = root / "18388_v9.pdf"
typst.compile(str(root / "main.typ"), output=str(out))
print("wrote", out, "bytes", out.stat().st_size)
