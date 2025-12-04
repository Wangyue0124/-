import json
import random
from typing import Dict, Any, List

OUT_PATH = "brand_sft.jsonl"
N_EXAMPLES = 40


BRAND_IDEAS = [
    "我想在台北開一間主打雞白湯的拉麵店，給上班族吃晚餐",
    "我想在學校附近開健康便當店，主打減脂高蛋白",
    "我想在台中開一間深夜營業的居酒屋拉麵",
    "我想在商辦區開沙拉吧，適合外帶午餐",
    "我想開一間主打素食拉麵的店，給不吃肉的人",
]

NAME_PREFIX = ["宵口", "一碗", "拾壹", "町口", "巷口", "晴日", "森川", "原味"]
NAME_SUFFIX_RAMEN = ["拉麵", "麵屋", "麵所", "湯屋"]
NAME_SUFFIX_BENTO = ["食堂", "餐盒", "便當", "良食"]
NAME_SUFFIX_SALAD = ["沙拉吧", "輕食", "沙拉研究所"]


def build_brand_from_idea(idea: str) -> Dict[str, Any]:
    idea = idea.strip()

    if "拉麵" in idea:
        store_type = "拉麵店"
        suffix = random.choice(NAME_SUFFIX_RAMEN)
        price_level = "$$"
        location_hint = "捷運站附近或上班族聚集的商辦區"
    elif "便當" in idea:
        store_type = "健康便當店"
        suffix = random.choice(NAME_SUFFIX_BENTO)
        price_level = "$$"
        location_hint = "學區或住宅區附近，方便外帶"
    elif "沙拉" in idea:
        store_type = "沙拉吧 / 輕食店"
        suffix = random.choice(NAME_SUFFIX_SALAD)
        price_level = "$$"
        location_hint = "商辦區或健身房周邊"
    else:
        store_type = "餐食店"
        suffix = "食堂"
        price_level = "$$"
        location_hint = "人流穩定的生活圈"

    brand_name = random.choice(NAME_PREFIX) + suffix
    brand_english_name = " ".join(["".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3)), "Ramen"])

    if "上班族" in idea or "商辦" in idea:
        target_customers = "附近上班族、加班族"
    elif "學校" in idea or "學生" in idea:
        target_customers = "大專院校學生與教職員"
    elif "素食" in idea:
        target_customers = "不吃肉或偏好蔬食的族群"
    else:
        target_customers = "附近常客與喜歡嚐鮮的年輕族群"

    slogan = f"{brand_name}，陪你撐過每一個忙碌的日常。"

    brand_story = (
        f"{brand_name} 想做的，不只是填飽肚子的一碗 {store_type.replace('店', '')}，"
        "而是讓你在忙碌生活裡有一個暫停鍵。"
        "我們用看得懂的食材組合與不太浮誇的價格，"
        "照顧你每天的真實胃口，而不是只為了打卡的一次性體驗。"
    )

    tone_keywords = ["溫暖", "不做作", "帶一點幽默感"]

    if "減脂" in idea or "高蛋白" in idea or "健康" in idea:
        menu = [
            {
                "name": "高蛋白舒肥雞胸餐盒",
                "english_name": "High Protein Chicken Bento",
                "description": "舒肥雞胸搭配原型澱粉與大量蔬菜，清爽又有飽足感。",
                "price_twd": 160,
                "tags": ["招牌", "高蛋白", "減脂友善"],
                "is_signature": True,
            },
            {
                "name": "地中海風味燉菜碗",
                "english_name": "Mediterranean Veggie Bowl",
                "description": "以番茄為基底的燉菜，搭配鷹嘴豆與全穀物，適合想少吃肉的客人。",
                "price_twd": 150,
                "tags": ["蔬食", "輕盈", "高纖"],
                "is_signature": False,
            },
        ]
    elif "居酒屋" in idea or "深夜" in idea:
        menu = [
            {
                "name": "炙燒叉燒豚骨拉麵",
                "english_name": "Flame Grilled Chashu Ramen",
                "description": "濃郁豚骨湯頭搭配炙燒叉燒與半熟蛋，適合深夜加班後的慰藉。",
                "price_twd": 260,
                "tags": ["招牌", "濃郁", "深夜限定"],
                "is_signature": True,
            },
            {
                "name": "明太子馬鈴薯沙拉",
                "english_name": "Mentaiko Potato Salad",
                "description": "帶一點鹹香辣度的開胃小菜，很適合搭配啤酒。",
                "price_twd": 120,
                "tags": ["小食", "下酒菜"],
                "is_signature": False,
            },
        ]
    else:
        menu = [
            {
                "name": "招牌雞白湯拉麵",
                "english_name": "Signature Chicken Paitan Ramen",
                "description": "以雞骨熬煮的白湯為基底，湯頭濃郁但不厚重，適合日常也適合偶爾犒賞自己。",
                "price_twd": 230,
                "tags": ["招牌", "人氣", "不容易膩"],
                "is_signature": True,
            }
        ]

    logo_prompt = (
        f"minimal ramen shop logo, {brand_english_name}, warm tone, simple line art, "
        "flat design, suitable for signboard and social media icon"
    )

    return {
        "brand_name": brand_name,
        "brand_english_name": brand_english_name,
        "slogan": slogan,
        "positioning": {
            "store_type": store_type,
            "target_customers": target_customers,
            "price_level": price_level,
            "location_hint": location_hint,
        },
        "logo_prompt": logo_prompt,
        "brand_story": brand_story,
        "tone_keywords": tone_keywords,
        "recommended_menu": menu,
    }


def main():
    instruction = (
        "你是一位餐飲品牌顧問，請根據使用者的開店想法，"
        "輸出品牌設定與推薦菜單（JSON 格式）。"
    )

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for _ in range(N_EXAMPLES):
            idea = random.choice(BRAND_IDEAS)
            out_json = build_brand_from_idea(idea)

            row = {
                "instruction": instruction,
                "input": json.dumps({"idea_zh": idea}, ensure_ascii=False),
                "output": json.dumps(out_json, ensure_ascii=False),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"已產生 {N_EXAMPLES} 筆品牌孵化 SFT 資料到 {OUT_PATH}")


if __name__ == "__main__":
    main()
