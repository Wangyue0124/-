import json
import random
from typing import Dict, Any, List

OUT_PATH = "biz_sft.jsonl"
N_EXAMPLES = 40  # 想多一點就改大


DISTRICTS = [
    "台北市大安區", "台北市信義區", "新北市板橋區", "新北市中和區",
    "桃園市中壢區", "台中市西屯區", "高雄市左營區",
]

RISK_WORDING = {
    "low": ["整體競爭壓力仍在可控範圍內", "短期內沒有明顯飽和風險"],
    "medium": ["已有初步飽和跡象，需要持續觀察", "競爭環境偏熱，必須主動優化"],
    "high": ["已屬高度競爭 / 接近飽和", "若不調整定位與菜單，獲利容易被侵蝕"],
}

ACTION_TEMPLATES = [
    {
        "title": "調整午晚高峰時段人力與備料",
        "owner_role": "店長",
        "eta_weeks": 2,
        "details": "根據近 30 天訂單尖峰時段，重新配置內外場人力與備料，提高尖峰時段接單能力。"
    },
    {
        "title": "針對高毛利品項加強套餐與加購設計",
        "owner_role": "行銷 / 企劃",
        "eta_weeks": 3,
        "details": "以高毛利主餐搭配飲品或小菜設計套餐，並於外送平台首頁與店內菜單提高曝光。"
    },
    {
        "title": "重新檢視表現不佳品項並規劃汰換",
        "owner_role": "店長 / 產品",
        "eta_weeks": 4,
        "details": "盤點近 60 天低點擊、低轉換品項，評估調整售價、份量或直接下架，集中資源在核心產品。"
    },
]


def random_internal_orders() -> Dict[str, Any]:
    base_orders = random.randint(4000, 20000)
    repeat_rate = round(random.uniform(0.25, 0.65), 2)
    delivery_ratio = round(random.uniform(0.3, 0.8), 2)

    top_items = [
        {"item_name": "舒肥雞胸餐盒", "order_count": int(base_orders * 0.22), "avg_margin": 0.32},
        {"item_name": "牛肉咖哩飯", "order_count": int(base_orders * 0.18), "avg_margin": 0.28},
        {"item_name": "鮭魚沙拉碗", "order_count": int(base_orders * 0.11), "avg_margin": 0.30},
    ]

    return {
        "total_orders_30d": base_orders,
        "unique_customers_30d": int(base_orders * random.uniform(0.2, 0.5)),
        "repeat_rate_30d": repeat_rate,
        "top_items": top_items,
        "delivery_ratio": delivery_ratio,
    }


def random_external_signals() -> Dict[str, Any]:
    competitor = random.randint(5, 30)
    new_openings = random.randint(0, 6)

    ramen_trend = random.choice(["hot", "rising", "flat"])
    healthy_trend = random.choice(["hot", "rising", "flat"])
    fried_trend = random.choice(["falling", "flat"])

    return {
        "competitor_count_within_1km": competitor,
        "new_openings_last_90d": new_openings,
        "office_worker_density": random.choice(["low", "medium", "high"]),
        "rent_trend": random.choice(["up", "flat", "down"]),
        "social_media_buzz": {
            "healthy_bento": healthy_trend,
            "fried_food": fried_trend,
            "ramen": ramen_trend,
        },
    }


def decide_risk_level(internal: Dict[str, Any], external: Dict[str, Any]) -> str:
    score = 0
    competitor = external["competitor_count_within_1km"]
    new_openings = external["new_openings_last_90d"]
    repeat_rate = internal["repeat_rate_30d"]

    if competitor >= 20:
        score += 2
    elif competitor >= 12:
        score += 1

    if new_openings >= 4:
        score += 1

    if repeat_rate < 0.3:
        score += 1

    if score <= 1:
        return "low"
    elif score == 2:
        return "medium"
    else:
        return "high"


def build_output(region: str, internal: Dict[str, Any], external: Dict[str, Any]) -> Dict[str, Any]:
    risk = decide_risk_level(internal, external)
    risk_sentence = random.choice(RISK_WORDING[risk])

    total_orders = internal["total_orders_30d"]
    competitor = external["competitor_count_within_1km"]
    repeat_rate = internal["repeat_rate_30d"]

    summary = (
        f"在{region}，過去 30 天累積約 {total_orders} 筆訂單，"
        f"周邊約有 {competitor} 間同類型店家，回購率約 {int(repeat_rate * 100)}%。"
        f"整體判斷為 {risk} 風險區間，{risk_sentence}。"
    )

    key_indicators: List[str] = [
        f"近 30 天總訂單量約 {total_orders} 筆",
        f"周邊競品數約 {competitor} 間",
        f"30 天回購率約 {int(repeat_rate * 100)}%"
    ]

    top_items = internal["top_items"]
    keep_items = [
        {
            "item_name": itm["item_name"],
            "reason": "訂單量穩定且毛利率不錯，建議持續作為核心品項。"
        }
        for itm in top_items[:2]
    ]

    fix_or_remove = [
        {
            "item_name": top_items[-1]["item_name"],
            "reason": "訂單占比相對較低，若製程複雜或備料成本高，可考慮調整作法或汰換。"
        }
    ]

    buzz = external["social_media_buzz"]
    new_item_ideas = []

    if buzz.get("healthy_bento") in ("hot", "rising"):
        new_item_ideas.append({
            "idea_name": "高蛋白健身餐盒",
            "description": "主打舒肥雞胸與低醣配菜，搭配簡單標示蛋白質與熱量。",
            "target_segment": "有健身習慣或在意身材的上班族",
            "positioning": "$$，午餐輕負擔、適合常態性訂購"
        })

    if buzz.get("ramen") in ("hot", "rising"):
        new_item_ideas.append({
            "idea_name": "期間限定風味拉麵",
            "description": "以現有湯頭為基礎調整配料，製作季節限定口味搭配社群宣傳。",
            "target_segment": "喜歡嘗鮮的年輕客群",
            "positioning": "$$，適合內用與社群打卡"
        })

    if not new_item_ideas:
        new_item_ideas.append({
            "idea_name": "商業午餐套餐",
            "description": "將熱銷主餐與飲品、小菜組成固定價格套餐，增加客單價。",
            "target_segment": "中午時間有限的上班族",
            "positioning": "$$，主打 CP 值與上菜速度"
        })

    action_items = random.sample(ACTION_TEMPLATES, k=2)

    return {
        "summary": summary,
        "market_saturation": {
            "risk_level": risk,
            "reason": risk_sentence,
            "key_indicators": key_indicators,
        },
        "menu_optimization": {
            "keep_items": keep_items,
            "fix_or_remove_items": fix_or_remove,
            "new_item_ideas": new_item_ideas,
        },
        "action_items": action_items,
    }


def main():
    instruction = (
        "你是一位連鎖餐飲商業顧問，請根據指定行政區的匯總訂單數據與外部市場訊號，"
        "輸出市場飽和評估與菜單優化建議（JSON 格式）。"
    )

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for _ in range(N_EXAMPLES):
            region = random.choice(DISTRICTS)
            internal = random_internal_orders()
            external = random_external_signals()
            out_json = build_output(region, internal, external)

            row = {
                "instruction": instruction,
                "input": json.dumps(
                    {
                        "region": region,
                        "internal_order_stats": internal,
                        "external_market_signals": external,
                    },
                    ensure_ascii=False,
                ),
                "output": json.dumps(out_json, ensure_ascii=False),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"已產生 {N_EXAMPLES} 筆商業顧問 SFT 資料到 {OUT_PATH}")


if __name__ == "__main__":
    main()
