import psycopg2
from src.APIhh import APIhh


class DBWorker:
    """Класс создания базы данных и таблиц."""

    def __init__(self, params: dict) -> None:
        self.params = params
        self.conn = None
        self.cur = None

    def create_database(self, database_name: str = "headhunter") -> None:
        """Создание БД и таблиц companies и vacancies"""
        print("Открытие соединения.")
        conn = psycopg2.connect(**self.params)
        conn.autocommit = True
        print("Создание ДБ.")

        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
            cur.execute(f"CREATE DATABASE {database_name}")

        conn.close()
        print("Закрытие соединения после создания БД.")

        print("Открытие нового соединения для БД.")
        self.conn = psycopg2.connect(database=database_name, **self.params)
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE companies (
                company_id INT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                website TEXT NOT NULL,
                vacancies INT NOT NULL
            )
        """)

        self.cur.execute("""
            CREATE TABLE vacancies (
                company_id INT REFERENCES companies(company_id),
                vacancy_id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                published_at DATE,
                salary_from INT,
                area VARCHAR(50) NOT NULL,
                type VARCHAR(50) NOT NULL
            )
        """)

        self.conn.commit()
        print("База данных и таблицы успешно созданы.")


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
                (company["id"],
                 company["name"],
                 company["url"],
                 company["open_vacancies"])
            )
            company_id = self.cur.fetchone()[0]

            vacancies = hh.get_vacancies(employer_id=company_id)

            for vacancy in vacancies:
                salary_from = vacancy["salary"]["from"] if vacancy["salary"] else None
                published_at = vacancy["published_at"][:10]
                self.cur.execute(
                    """
                    INSERT INTO vacancies (company_id, 
                            vacancy_id, name, published_at, salary_from, area, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (vacancy_id) DO NOTHING""",
                    (company_id,
                     vacancy["id"],
                     vacancy["name"],
                     published_at,
                     salary_from,
                     vacancy["area"]["name"],
                     vacancy["type"]["name"])
                )
            self.conn.commit()
            print("Данные успешно загружены в базу данных.")

    def close(self):
        """Закрытие курсора и соединения"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Соединение закрыто.")


