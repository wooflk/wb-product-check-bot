from core import *

def test_case_1():
        article = 275016564

        return get_product(article) != None

def test_case_2():
        article = 0000000000

        return get_product(article) == None


if __name__ == "__main__":
               print(test_case_1())
               print(test_case_2())
