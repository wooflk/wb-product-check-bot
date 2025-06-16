from core import get_product

def test_case_1():
    article = 275016564  # реально существующий артикул
    result = get_product(article)
    return isinstance(result, str) and "товар не найден" not in result.lower()

def test_case_2():
    article = 99999999999999  # несуществующий
    result = get_product(article)
    return isinstance(result, str) and "товар не найден" in result.lower()

if __name__ == "__main__":
    print("test_case_1 passed:", test_case_1())
    print("test_case_2 passed:", test_case_2())
