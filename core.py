import requests
from config import RUB_TO_KZT

def get_product(art):
    art_id = str(art)
    first_id = art_id[:4]
    second_id = art_id[:6]

    product_url = f'https://alm-basket-cdn-01.geobasket.ru/vol{first_id}/part{second_id}/{art}/info/ru/card.json'
    price_url = f'https://basket-17.wbbasket.ru/vol{first_id}/part{second_id}/{art}/info/price-history.json'

    try:
        response = requests.get(product_url)
        if response.status_code != 200:
            return "извини, солнце, но товар не найден!"

        data = response.json()
        name = data.get("imt_name")
        brand = data.get("selling", {}).get("brand_name") or "бренд не указан"
        desc = data.get("description") or "описание не указано"
        compositions = data.get("compositions")
        imt_id = data.get("imt_id")

        if isinstance(compositions, list) and compositions:
            comp_names = [i["name"] for i in compositions if "name" in i]
            compositions = ", ".join(comp_names) if comp_names else "состав не указан"
        else:
            compositions = "состав, к сожалению, не указан"

        price_info = "нет данных"
        average_price = None
        current_price = None
        verdict = ""

        try:
            price_response = requests.get(price_url)
            if price_response.status_code == 200:
                price_data = price_response.json()
                rub_prices = [i.get("price", {}).get("RUB") for i in price_data if i.get("price", {}).get("RUB")]
                if rub_prices:
                    average_price = sum(rub_prices) / len(rub_prices)
                    current_price = rub_prices[-1]

                    kzt_prices = [int(p / 100) * RUB_TO_KZT for p in rub_prices]
                    price_info = ", ".join(map(str, kzt_prices))
        except Exception as e:
            return f"ошибка получения цены: {e}"

        if average_price and current_price:
            avg_kzt = average_price * RUB_TO_KZT
            curr_kzt = current_price * RUB_TO_KZT
            if curr_kzt < avg_kzt:
                verdict = "сейчас выгодно покупать!!"
            elif curr_kzt > avg_kzt:
                verdict = "немного дорого, покупать невыгодно"
            else:
                verdict = "цена средненькая"
        else:
            avg_kzt = curr_kzt = 0

        rating = None
        feedbacks = None
        try:
            review_response = requests.get("https://card.wb.ru/cards/v2/list", params={
                "appType": 1,
                "curr": "kzt",
                "dest": 269,
                "spp": 30,
                "hide_dtype": "10;13;14",
                "ab_testing": "false",
                "lang": "ru",
                "nm": art_id,
                "ignore_stocks": "true"
            })
            if review_response.status_code == 200:
                res = review_response.json()
                products = res.get("data", {}).get("products", [])
                if products:
                    rating = products[0].get("reviewRating", "нет данных")
                    feedbacks = products[0].get("feedbacks", "нет данных")
        except Exception as e:
            return f"ошибка получения рейтинга: {e}"

        rating_block = ""
        if rating and feedbacks:
            try:
                feedbacks = int(feedbacks)
                rating = float(rating)

                if feedbacks < 10:
                    trust = "слишком мало отзывов — доверие низкое"
                elif feedbacks < 50:
                    trust = "мало отзывов — доверие умеренное"
                elif feedbacks < 200:
                    trust = "достаточно отзывов — рейтинг заслуживает внимания"
                else:
                    trust = "много отзывов — высокий уровень доверия"

                if rating >= 4.5:
                    grade = "высокий рейтинг"
                elif rating >= 4.0:
                    grade = "нормальный рейтинг"
                elif rating >= 3.0:
                    grade = "средний рейтинг"
                else:
                    grade = "низкий рейтинг"

                rating_block = f"\n *оценка:* {rating} — {grade}\n{feedbacks} отзывов, {trust}\n\n"

            except Exception:
                rating_block = f"\n *оценка:* {rating} — {feedbacks} отзывов\n\n"

        questions_text = ""
        questions_text = "\n(не удалось загрузить вопросы)"
        try:
            qna_response = requests.get(
                "https://questions.wildberries.ru/api/v1/questions",
                params={"imtId": imt_id, "take": 5, "skip": 0},
                timeout=5
            )
            data_q = qna_response.json()
            questions = data_q.get("questions", [])
            if questions:
                questions_text = "\n*вопросы покупателей*:\n"
                for q in questions:
                    question = q.get("text", "").strip()
                    answer = q.get("answer", "").get("text", "").strip()
                    if question:
                        questions_text += f"- *вопрос:* {question}\n"
                        if answer:
                            questions_text += f'- *ответ:* {answer} \n \n'
            else:
                questions_text = "\nвопросов нет."
        except Exception as e:
            questions_text = f"\nошибка при получении вопросов: {e}"

        return (
            f"*{name}*\n"
            f"*бренд*: {brand}\n"
            f"{rating_block}"
            f"\n *состав* : {compositions}\n"
            f"\n *описание*:\n{desc[:500]}...\n"
            f"\n *история цен (тенге)*: {price_info}\n"
            f"*текущая цена*: {curr_kzt / 100:.2f} \n"
            f"*средняя цена*: {avg_kzt / 100:.2f} \n"
            f"{verdict}\n"
            f"{questions_text}"
        )

    except Exception as e:
        return f"ошибка данных: {e}"
