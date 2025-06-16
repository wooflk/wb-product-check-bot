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

        if isinstance(compositions, list) and compositions:
            comp_names = []
            for i in compositions:
                if "name" in i:
                    comp_names.append(i["name"])
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
                if isinstance(price_data, list) and price_data:
                    rub_prices = []
                    for i in price_data:
                        price = i.get("price", {}).get("RUB")
                        if price:
                            rub_prices.append(price)

                    if rub_prices:
                        average_price = sum(rub_prices) / len(rub_prices)
                        current_price = rub_prices[-1]

                        kzt_prices = []
                        for rub in rub_prices:
                            converted = int(rub /100) * RUB_TO_KZT
                            kzt_prices.append(str(converted))
                        
                        price_info = ", ".join(kzt_prices)
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

        return (
            f"*{name}*\n"
            f"бренд: _{brand}_\n\n"
            f"состав: {compositions}\n\n"
            f"описание:\n{desc[:500]}...\n\n"
            f"история цен (тенге): {price_info}\n"
            f"текущая цена: {curr_kzt / 100} \n"
            f"средняя цена: {avg_kzt / 100} \n"
            f"{verdict}"
        )
    
    except Exception as e:
        return f"ошибка данных: {e}"
