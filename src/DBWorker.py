from json import JSONDecodeError

import psycopg2

from src.APIhh import APIhh
from utils.read_from_file import read_test_data, test_data_file

REQUIRED_COMPANY_FIELDS = {
    "company_id",
    "name",
    "website",
    "vacancies",
}

REQUIRED_VACANCY_FIELDS = {
    "company_id",
    "vacancy_id",
    "name",
    "published_at",
    "salary_from",
    "area",
    "type",
    "website",
}


class TestDataError(Exception):
    """Ошибка загрузки тестовых данных."""


class DBWorker:
    """Класс создания базы данных и таблиц."""

    def __init__(self, params: dict) -> None:
        self.params = params
        self.conn = None
        self.cur = None

    def create_database(self, database_name: str = "headhunter") -> str:
        """Создание БД и таблиц companies и vacancies"""
        conn = psycopg2.connect(**self.params)
        conn.autocommit = True

        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (database_name,),
            )

            database_exists = cur.fetchone() is not None

            if not database_exists:
                cur.execute(f"CREATE DATABASE {database_name}")
                message = f"База данных '{database_name}' создана."

            else:
                message = f"База данных '{database_name}' уже существует."

        conn.close()

        self.conn = psycopg2.connect(database=database_name, **self.params)
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                company_id INT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                website TEXT NOT NULL,
                vacancies INT NOT NULL
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                company_id INT REFERENCES companies(company_id),
                vacancy_id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                published_at DATE,
                salary_from INT,
                area VARCHAR(50) NOT NULL,
                type VARCHAR(50) NOT NULL,
                website TEXT NOT NULL
            )
        """)

        self.conn.commit()

        return message

    def save_to_db(self, employer_name) -> None:
        """Заполнение данными таблиц vacancies и employers"""
        print("Сохранение данных в ДБ.")
        hh = APIhh()
        employers = hh.get_employers(employer_name)

        for company in employers:
            self.cur.execute(
                """
                INSERT INTO companies (company_id, name, website, vacancies) 
                VALUES (%s, %s, %s, %s) 
                RETURNING company_id""",
                (company["id"], company["name"], company["url"], company["open_vacancies"]),
            )
            company_id = self.cur.fetchone()[0]

            vacancies = hh.get_vacancies(employer_id=company_id)

            for vacancy in vacancies:
                salary_from = vacancy["salary"]["from"] if vacancy["salary"] else None
                published_at = vacancy["published_at"][:10]
                self.cur.execute(
                    """
                    INSERT INTO vacancies (company_id, 
                            vacancy_id, name, published_at, salary_from, area, type, website)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (vacancy_id) DO NOTHING""",
                    (
                        company_id,
                        vacancy["id"],
                        vacancy["name"],
                        published_at,
                        salary_from,
                        vacancy["area"]["name"],
                        vacancy["type"]["name"],
                        vacancy["apply_alternate_url"],
                    ),
                )
            self.conn.commit()
        print("Данные успешно сохранены.")

    def close(self) -> None:
        """Закрытие курсора и соединения"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def validate_test_data(self, test_data: dict) -> None:
        """Проверка структуры тестовых данных."""

        if "companies" not in test_data:
            raise TestDataError("В тестовых данных отсутствует раздел 'companies'.")

        if "vacancies" not in test_data:
            raise TestDataError("В тестовых данных отсутствует раздел 'vacancies'.")

        for index, company in enumerate(test_data["companies"], start=1):
            missing_fields = REQUIRED_COMPANY_FIELDS - company.keys()

            if missing_fields:
                fields = ", ".join(sorted(missing_fields))
                raise TestDataError(f"Компания №{index}: отсутствуют поля: {fields}.")

        for index, vacancy in enumerate(test_data["vacancies"], start=1):
            missing_fields = REQUIRED_VACANCY_FIELDS - vacancy.keys()

            if missing_fields:
                fields = ", ".join(sorted(missing_fields))
                raise TestDataError(f"Вакансия №{index}: отсутствуют поля: {fields}.")

    def save_test_data(self) -> None:
        """Очистка таблиц и заполнение БД тестовыми данными."""

        print("Загрузка тестовых данных в БД.")

        try:
            test_data = read_test_data(test_data_file)
            self.validate_test_data(test_data)

        except FileNotFoundError as e:
            raise TestDataError(f"Файл тестовых данных не найден: {test_data_file}") from e

        except JSONDecodeError as e:
            raise TestDataError(f"Ошибка формата JSON: строка {e.lineno}, столбец {e.colno}") from e

        try:
            self.cur.execute("""
                TRUNCATE TABLE vacancies, companies CASCADE
            """)

            for company in test_data["companies"]:
                self.cur.execute(
                    """
                    INSERT INTO companies (
                        company_id, 
                        name, 
                        website, 
                        vacancies
                    ) VALUES (%s, %s, %s, %s) 
                """,
                    (company["company_id"], company["name"], company["website"], company["vacancies"]),
                )

            for vacancy in test_data["vacancies"]:
                self.cur.execute(
                    """
                    INSERT INTO vacancies (
                        company_id, 
                        vacancy_id, 
                        name,
                        published_at, 
                        salary_from, 
                        area,
                        type,
                        website
                        )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        vacancy["company_id"],
                        vacancy["vacancy_id"],
                        vacancy["name"],
                        vacancy["published_at"],
                        vacancy["salary_from"],
                        vacancy["area"],
                        vacancy["type"],
                        vacancy["website"],
                    ),
                )

                self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

        print("Тестовые данные успешно сохранены.")
