from tabulate import tabulate

from src.APIhh import HHApiError
from src.DBManager import DBManager
from src.DBWorker import DBWorker, TestDataError
from utils.config import Config
from utils.read_from_file import path_file, read_companies_from_file


def format_salary(salary):
    """Красиво форматирует зарплату"""
    if salary is None:
        salary_text = "Нет данных"
    else:
        salary_text = f"{salary:,}".replace(",", " ")
    return salary_text


def user_interface(database_created=None):
    """Основное меню взаимодействия с пользователем"""

    print("""
Вас приветствует менеджер по работе с базой данных. 
""")

    while True:
        print("""
Выберите действие:
1 - Создать базу данных
2 - Загрузить тестовые данные
3 - Загрузить данные с HH.ru
4 - Далее
0 - Выход
""")
        choice = input("Введите номер пункта: ")

        if choice == "1":
            db = DBWorker(Config.DB_PARAMS)
            db.create_database()
            message = db.create_database()
            print(message)
            db.close()

        elif choice == "2":
            db = DBWorker(Config.DB_PARAMS)

            try:
                db.create_database()
                db.save_test_data()

            except TestDataError as e:
                print(f"\nОшибка загрузки тестовых данных: {e}")

            finally:
                db.close()

        elif choice == "3":
            db = DBWorker(Config.DB_PARAMS)

            try:
                db.create_database()

                companies = read_companies_from_file(path_file)
                db.save_to_db(companies)

            except HHApiError as e:
                print(f"\nОшибка загрузки данных с HH.ru: {e}")

            finally:
                db.close()

        elif choice == "4":
            db = DBManager("headhunter", Config.DB_PARAMS)

            while True:
                print("""
Выберите действие:
1 - Список компаний и количество вакансий
2 - Все вакансии
3 - Средняя зарплата по компаниям
4 - Вакансии с зарплатой выше средней
5 - Вакансии по ключевому слову
0 - Выход
                        """)
                choice = input("Введите номер пункта: ")

                if choice == "1":
                    data = db.get_companies_and_vacancies_count()
                    print("\nКомпании и количество вакансий:")
                    print(
                        tabulate(data, headers=["Компания", "Количество вакансий"], tablefmt="pretty", stralign="left")
                    )

                elif choice == "2":
                    data = db.get_all_vacancies()
                    print("\nВсе вакансии:")
                    formatted = [
                        (company, vacancy, format_salary(salary), url) for company, vacancy, salary, url in data
                    ]
                    print(
                        tabulate(
                            formatted,
                            headers=["Компания", "Вакансия", "Зарплата, руб.", "Интернет сайт"],
                            tablefmt="pretty",
                            stralign="left",
                        )
                    )

                elif choice == "3":
                    data = db.get_avg_salary()
                    print("\nСредняя зарплата по компаниям:")
                    formatted = [(company, format_salary(salary)) for company, salary in data]
                    print(
                        tabulate(
                            formatted,
                            headers=["Компания", "Средняя зарплата, руб."],
                            tablefmt="pretty",
                            stralign="left",
                        )
                    )

                elif choice == "4":
                    data = db.get_vacancies_with_higher_salary()
                    print("\nВакансии с зарплатой выше средней:")
                    formatted = [(company, vacancy, format_salary(salary)) for company, vacancy, salary in data]
                    print(
                        tabulate(
                            formatted,
                            headers=["Компания", "Вакансия", "Зарплата, руб."],
                            tablefmt="pretty",
                            stralign="left",
                        )
                    )

                elif choice == "5":
                    print("\nПолучение вакансий по ключевому слову")
                    user_input = input(
                        "Введите слово для поиска вакансий (По умолчанию выводится весь список вакансий): "
                    )
                    data = db.get_vacancies_with_keyword(user_input)
                    formatted = [(company, vacancy, format_salary(salary)) for company, vacancy, salary in data]
                    print(
                        tabulate(
                            formatted,
                            headers=["Компания", "Вакансия", "Зарплата, руб."],
                            tablefmt="pretty",
                            stralign="left",
                        )
                    )

                elif choice == "0":
                    print("Выход из программы")
                    db.close()
                    return

                else:
                    print("Неверный ввод, попробуйте снова.")

        elif choice == "0":
            print("Выход из программы")
            break

        else:
            print("Неверный ввод, попробуйте снова.")
