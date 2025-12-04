import json
import random
from typing import Dict, Any, List


N_EXAMPLES = 50          # 要產生幾筆訓練樣本
OUT_PATH = "diet_sft.jsonl"
DATA_PATH = "nutrition_dataset.json"


def load_food_db(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    restaurants = data["restaurants"]
    dishes = data["dishes"]
    rest_by_id = {r["restaurant_id"]: r for r in restaurants}
    return restaurants, dishes, rest_by_id


def random_user_profile() -> Dict[str, Any]:
    gender = random.choice(["male", "female"])
    height = random.randint(155, 185)
    weight = random.randint(50, 95)
    age = random.randint(18, 40)
    activity = random.choice(["sedentary", "lightly_active", "active"])

    return {
        "height_cm": height,
        "weight_kg": weight,
        "age": age,
        "gender": gender,
        "activity_level": activity,
    }


def random_goal() -> Dict[str, str]:
    # 內部用英文，instruction 用中文
    choices = [
        ("減脂", "fat_loss"),
        ("增肌", "muscle_gain"),
        ("健康均衡", "general_health"),
    ]
    return random.choice(choices)


def estimate_daily_calories(user: Dict[str, Any], goal_internal: str) -> int:
    # 超簡化估算：24 * 體重，再依目標微調
    weight = user["weight_kg"]
    base = 24 * weight

    if goal_internal == "fat_loss":
        base -= 400
    elif goal_internal == "muscle_gain":
        base += 200

    base = max(1200, min(2600, int(base)))
    return base


def pick_candidate_dishes(dishes: List[Dict[str, Any]], goal_internal: str) -> List[Dict[str, Any]]:
    if goal_internal == "fat_loss":
        cands = [
            d for d in dishes
            if d["calories_kcal"] <= 650 and "減脂友善" in d.get("tags", [])
        ]
        return cands or dishes
    elif goal_internal == "muscle_gain":
        cands = [
            d for d in dishes
            if d["protein_g"] >= 25
        ]
        return cands or dishes
    else:
        return dishes


def build_fake_week_plan(
    user_profile: Dict[str, Any],
    goal_zh: str,
    goal_internal: str,
    dishes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    target = estimate_daily_calories(user_profile, goal_internal)
    candidates = pick_candidate_dishes(dishes, goal_internal)
    if len(candidates) < 30:
        candidates = dishes

    weekly_menu = []

    for day in range(1, 8):
        day_meals = []
        total_cal = 0

        # 每天 2～3 餐
        n_meals = random.choice([2, 3])
        meal_types = ["breakfast", "lunch", "dinner"]
        chosen_meal_types = meal_types[:n_meals]

        for mt in chosen_meal_types:
            dish = random.choice(candidates)
            total_cal += dish["calories_kcal"]
            note_parts = []

            if "高蛋白" in dish.get("tags", []):
                note_parts.append("高蛋白")
            if "減脂友善" in dish.get("tags", []):
                note_parts.append("減脂友善")
            if dish.get("carbon_footprint_label") == "low":
                note_parts.append("低碳足跡")

            if not note_parts:
                note_parts.append("一般建議")

            day_meals.append({
                "meal_type": mt,
                "dish_id": dish["dish_id"],
                "restaurant_id": dish["restaurant_id"],
                "note": "、".join(note_parts),
            })

        weekly_menu.append({
            "day": day,
            "total_calories": total_cal,
            "meals": day_meals,
        })

    result = {
        "goal": goal_internal,
        "user_profile": user_profile,
        "daily_calorie_target": target,
        "weekly_menu": weekly_menu,
        "note": f"此菜單為自動產生，用於訓練示範（目標：{goal_zh}）",
    }
    return result


def build_instruction(goal_zh: str) -> str:
    if "減脂" in goal_zh:
        return "你是一位飲食管家，依照使用者需求設計一週減脂外食菜單，輸出 JSON。"
    elif "增肌" in goal_zh:
        return "你是一位飲食管家，依照使用者需求設計一週增肌外食菜單，輸出 JSON。"
    else:
        return "你是一位飲食管家，依照使用者需求設計一週健康均衡外食菜單，輸出 JSON。"


def main():
    restaurants, dishes, rest_by_id = load_food_db(DATA_PATH)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for _ in range(N_EXAMPLES):
            user_profile = random_user_profile()
            goal_zh, goal_internal = random_goal()

            # 建 input：主要放目標 + 使用者資料；必要時也可以加部分菜色資訊
            input_obj = {
                "goal": goal_internal,
                "user_profile": user_profile,
                # 想要也可以加食物樣本，但這裡先不塞，避免 prompt 太長
                # "food_db_sample": random.sample(dishes, k=min(40, len(dishes))),
            }

            output_obj = build_fake_week_plan(
                user_profile=user_profile,
                goal_zh=goal_zh,
                goal_internal=goal_internal,
                dishes=dishes,
            )

            row = {
                "instruction": build_instruction(goal_zh),
                "input": json.dumps(input_obj, ensure_ascii=False),
                "output": json.dumps(output_obj, ensure_ascii=False),
            }

            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"已產生 {N_EXAMPLES} 筆訓練資料到 {OUT_PATH}")


if __name__ == "__main__":
    main()
