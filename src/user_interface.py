from src.DBManager import DBManager
from utils.config import Config
from tabulate import tabulate

def format_salary(salary):
    """Красиво форматирует зарплату"""
    if salary is None:
        salary_text = "Нет данных"
    else:
        salary_text = f"{salary:,}".replace(",", " ")
    return salary_text


def user_interface():
    """Основное меню взаимодействия с пользователем"""
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
            # for name, vacancies in data:
                # print(f"{name}: {vacancies} вакансий")

            print(tabulate(data, headers=["Компания", "Количество вакансий"], tablefmt="pretty", stralign="left"))

        elif choice == "2":
            data = db.get_all_vacancies()
            print("\nВсе вакансии:")
            formatted = [(company, vacancy, format_salary(salary)) for company, vacancy, salary in data]
            # for name, salary, area in data:
            #     print(f"{name} | {area} | {salary if salary else 'Нет данных'} руб.")
            print(tabulate(formatted, headers=["Компания", "Вакансия", "Зарплата, руб."], tablefmt="pretty", stralign="left"))


        elif choice == "3":
            data = db.get_avg_salary()
            print("\nСредняя зарплата по компаниям:")
            formatted = [(company, format_salary(salary)) for company, salary in data]
            # for name, salary in data:
            #     if salary is None:
            #         salary_text = "Нет данных"
            #     else:
            #         salary_text = f"{salary:,}".replace(",", " ") + " руб."
            print(tabulate(formatted, headers=["Компания", "Средняя зарплата, руб."], tablefmt="pretty", stralign="left"))

        elif choice == "4":
            data = db.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:")
            formatted = [(company, vacancy, format_salary(salary)) for company, vacancy, salary in data]
            # for name, salary in data:
            #     if salary is None:
            #         salary_text = "Нет данных"
            #     else:
            #         salary_text = f"{salary:,}".replace(",", " ") + " руб."
            print(tabulate(formatted, headers=["Компания", "Вакансия", "Зарплата, руб."], tablefmt="pretty", stralign="left"))

        elif choice == "5":
            print("\nПолучение вакансий по ключевому слову")
            user_input = input("Введите слово для поиска вакансий: ")
            data = db.get_vacancies_with_keyword(user_input)
            formatted = [(company, vacancy, format_salary(salary)) for company, vacancy, salary in data]
            # for name, vacancies, salary in data:
            #     print(f"{name} | {vacancies} | {salary if salary else 'нет данных'} руб.")
            print(tabulate(formatted, headers=["Компания", "Вакансия", "Зарплата, руб."], tablefmt="pretty", stralign="left"))

        elif choice == "0":
            print("Выход из программы")
            break

        else:
            print("Неверный ввод, попробуйте снова.")

