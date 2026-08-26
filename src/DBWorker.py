import psycopg2

from utils.read_from_file import read_test_data
from utils.read_from_file import test_data_file

from src.APIhh import APIhh


class DBWorker:
    """Класс создания базы данных и таблиц."""

    def __init__(self, params: dict) -> None:
        self.params = params
        self.conn = None
        self.cur = None

    def create_database(self, database_name: str = "headhunter") -> None:
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
                print(f"База данных '{database_name}' не существует. Создание БД.")
                cur.execute(f"CREATE DATABASE {database_name}")

            else:
                print(f"База данных '{database_name}' уже существует.")

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


    def save_test_data(self) -> None:
        """Очистка таблиц и заполнение БД тестовыми данными."""

        print("Загрузка тестовых данных в БД.")

        test_data = read_test_data(test_data_file)

        self.cur.execute("""
            TRUNCATE TABLE vacancies, companies CASCADE
        """)

        for company in test_data["companies"]:
            self.cur.execute("""
                INSERT INTO companies (
                    company_id, 
                    name, 
                    website, 
                    vacancies
                ) VALUES (%s, %s, %s, %s) 
            """,(
                company["company_id"],
                company["name"],
                company["website"],
                company["vacancies"]
            ),
                             )

        for vacancy in test_data["vacancies"]:
            self.cur.execute("""
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
            """,(
                vacancy["company_id"],
                vacancy["vacancy_id"],
                vacancy["name"],
                vacancy["published_at"],
                vacancy["salary_from"],
                vacancy["area"],
                vacancy["type"],
                vacancy["website"],
            )
                             )

            self.conn.commit()

        print("Тестовые данные успешно сохранены.")
