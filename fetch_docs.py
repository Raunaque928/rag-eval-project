"""Downloads the FastAPI docs (markdown) into data/docs. Needs git installed."""
import os, shutil, stat, subprocess, pathlib

TMP = pathlib.Path("data/_fastapi_repo")
OUT = pathlib.Path("data/docs")

def _force_remove(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

if OUT.exists() and any(OUT.rglob("*.md")):
    print("Docs already present in data/docs, skipping.")
    raise SystemExit

subprocess.run(["git", "clone", "--depth", "1", "https://github.com/fastapi/fastapi", str(TMP)], check=True)
src = TMP / "docs" / "en" / "docs"
for p in src.rglob("*.md"):
    dest = OUT / p.relative_to(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(p, dest)
shutil.rmtree(TMP, onerror=_force_remove)
print(f"Done. {len(list(OUT.rglob('*.md')))} markdown files in {OUT}")
