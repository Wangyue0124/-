import json
from pathlib import Path
from typing import List

OUT_PATH = "all_sft.jsonl"

SOURCES: List[str] = [
    "diet_sft.jsonl",
    "biz_sft.jsonl",
    "brand_sft.jsonl",
]


def main():
    total = 0

    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for src in SOURCES:
            path = Path(src)
            if not path.exists():
                print(f"警告：找不到 {src}，略過")
                continue

            print(f"合併資料來源：{src}")
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    if not all(k in obj for k in ("instruction", "input", "output")):
                        continue
                    out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                    total += 1

    print(f"已合併產生 {OUT_PATH}，共 {total} 筆樣本。")


if __name__ == "__main__":
    main()
