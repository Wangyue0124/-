import json
import random

AREAS = [
    "台北市大安區", "台北市信義區", "新北市板橋區", "新北市中和區",
    "桃園市中壢區", "台中市西屯區", "高雄市左營區"
]

CUISINES = [
    "健康餐盒", "沙拉", "早午餐", "日式便當", "義大利麵", "咖哩飯", "輕食三明治"
]

# 用來決定碳足跡區間（只是大致範圍）
PROTEIN_TYPES = {
    "chicken": (0.9, 1.7),
    "pork":    (1.3, 2.2),
    "beef":    (2.5, 5.0),
    "fish":    (0.8, 1.6),
    "egg":     (0.5, 1.0),
    "tofu":    (0.3, 0.8),
    "veg":     (0.2, 0.6),
    "mixed":   (0.8, 2.0),
}

DISH_TEMPLATES = [
    ("烤雞胸餐盒", "chicken", "main"),
    ("舒肥雞胸沙拉", "chicken", "main"),
    ("牛肉咖哩飯", "beef", "main"),
    ("豬排咖哩飯", "pork", "main"),
    ("鮭魚沙拉飯", "fish", "main"),
    ("和風雞腿便當", "chicken", "main"),
    ("照燒豬肉便當", "pork", "main"),
    ("嫩煎牛排餐盤", "beef", "main"),
    ("豆腐什錦沙拉", "tofu", "main"),
    ("綜合烤時蔬餐盒", "veg", "main"),
    ("蔬菜歐姆蛋套餐", "egg", "main"),
    ("鮭魚溫沙拉", "fish", "main"),
    ("藜麥雞胸碗", "chicken", "main"),
    ("藜麥豆腐碗", "tofu", "main"),
    ("地中海蔬菜盤", "veg", "main"),
    ("雞胸佛陀碗", "chicken", "main"),
    ("鷹嘴豆沙拉碗", "veg", "main"),
    ("莓果優格碗", "veg", "side"),
    ("原味優格杯", "veg", "side"),
    ("堅果綜合沙拉", "veg", "side"),
    ("水煮蛋雙拼", "egg", "side"),
    ("清炒時蔬", "veg", "side"),
    ("烤地瓜", "veg", "side"),
    ("無糖冷泡茶", "veg", "drink"),
    ("無糖綠茶", "veg", "drink"),
    ("檸檬氣泡水", "veg", "drink"),
    ("豆漿燕麥飲", "tofu", "drink"),
]

SPICY_WORDS = ["麻辣", "香辣", "微辣"]
HEALTH_PREFIX = ["低脂", "高蛋白", "減糖", "原型食物", "輕盈"]
VEG_MARK = ["全素", "蛋奶素", "蔬食"]


def random_restaurants(n_rest=50):
    restaurants = []
    for rid in range(1, n_rest + 1):
        prefix = random.choice(["陽光", "元氣", "小巷", "初晨", "良食", "森活", "便當研究所", "深夜"])
        suffix = random.choice(["食堂", "廚房", "便當", "餐盒", "輕食", "沙拉吧", "咖啡館"])
        name = prefix + suffix

        restaurants.append({
            "restaurant_id": rid,
            "name": name,
            "area": random.choice(AREAS),
            "cuisine_type": random.choice(CUISINES),
            "avg_price": random.randint(120, 260),
            "tags": random.sample(
                ["健康", "高蛋白", "低醣", "少油", "素食友善", "外帶方便", "環保餐具"],
                k=random.randint(2, 4)
            ),
            "has_delivery": random.choice([True, False]),
            "has_b2b_service": random.choice([True, False])
        })
    return restaurants


def carbon_footprint_for_protein(protein_type: str) -> float:
    low, high = PROTEIN_TYPES.get(protein_type, PROTEIN_TYPES["mixed"])
    return round(random.uniform(low, high), 2)


def carbon_label(value: float) -> str:
    if value < 0.8:
        return "low"
    elif value < 1.6:
        return "medium"
    else:
        return "high"


def gen_macros(calories: int, category: str):
    if category == "drink":
        protein = random.randint(2, 8)
        fat = random.randint(0, 5)
    elif category == "side":
        protein = random.randint(4, 15)
        fat = random.randint(2, 10)
    else:  # main
        protein = random.randint(18, 45)
        fat = random.randint(8, 22)

    remaining = max(calories - (protein * 4 + fat * 9), 40)
    carbs = max(0, int(remaining / 4))
    return protein, carbs, fat


def gen_dishes(restaurants, n_dishes=300):
    dishes = []
    dish_id = 1

    while dish_id <= n_dishes:
        rest = random.choice(restaurants)
        base_name, protein_type, category = random.choice(DISH_TEMPLATES)

        name_parts = []

        if random.random() < 0.4:
            name_parts.append(random.choice(HEALTH_PREFIX))

        if protein_type in ("veg", "tofu", "egg") and random.random() < 0.4:
            name_parts.append(random.choice(VEG_MARK))

        spicy = False
        if random.random() < 0.25:
            spicy = True
            name_parts.append(random.choice(SPICY_WORDS))

        name_parts.append(base_name)
        full_name = "".join(name_parts)

        if category == "main":
            calories = random.randint(380, 850)
        elif category == "side":
            calories = random.randint(120, 350)
        else:
            calories = random.randint(0, 180)

        protein_g, carbs_g, fat_g = gen_macros(calories, category)
        cf = carbon_footprint_for_protein(protein_type)
        cf_label = carbon_label(cf)

        is_veg = protein_type in ("veg", "tofu", "egg")
        is_vegan = protein_type in ("veg", "tofu")

        tags = []
        if protein_g >= 25:
            tags.append("高蛋白")
        if carbs_g <= 40 and category == "main":
            tags.append("低醣")
        if calories <= 550 and category == "main":
            tags.append("減脂友善")
        if cf_label == "low":
            tags.append("低碳足跡")
        if spicy:
            tags.append("辣")

        dish = {
            "dish_id": dish_id,
            "restaurant_id": rest["restaurant_id"],
            "name": full_name,
            "category": category,
            "cuisine_type": rest["cuisine_type"],
            "calories_kcal": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "carbon_footprint_kg_co2e": cf,
            "carbon_footprint_label": cf_label,
            "is_spicy": spicy,
            "is_vegetarian": is_veg,
            "is_vegan": is_vegan,
            "tags": tags,
            "allergens": random.sample(
                ["egg", "milk", "soy", "nuts", "gluten"],
                k=random.randint(0, 2)
            )
        }

        dishes.append(dish)
        dish_id += 1

    return dishes


def main(out_path="nutrition_dataset.json"):
    restaurants = random_restaurants(50)
    dishes = gen_dishes(restaurants, 300)
    data = {
        "restaurants": restaurants,
        "dishes": dishes
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已產生假資料：{out_path}，餐廳 {len(restaurants)} 間、菜色 {len(dishes)} 道。")


if __name__ == "__main__":
    main()
