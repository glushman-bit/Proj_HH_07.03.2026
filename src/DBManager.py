import psycopg2


class DBManager:
    """Класс для работы с БД"""

    def __init__(self, dbname, params):
        self.conn = psycopg2.connect(dbname=dbname, **params)
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self):
        """Получение списка компаний и количество вакансий у каждой компании"""
        self.cur.execute("""
            SELECT name, vacancies
            FROM companies
            ORDER BY vacancies DESC
            """)
        return self.cur.fetchall()

    def get_all_vacancies(self):
        """Получение всех вакансий"""
        self.cur.execute("""
            SELECT com.name, vac.name, vac.salary_from, vac.website
            FROM vacancies vac
            INNER JOIN companies com USING(company_id)
            WHERE vac.salary_from IS NOT NULL
            """)
        return self.cur.fetchall()

    def get_avg_salary(self):
        """Получение среднего значения зарплаты"""
        self.cur.execute("""
            SELECT com.name, ROUND(AVG(vac.salary_from)) AS avg_salary
            FROM vacancies vac
            LEFT JOIN companies com USING(company_id)
            GROUP BY com.name
            ORDER BY avg_salary DESC NULLS LAST
        """)
        return self.cur.fetchall()

    def get_vacancies_with_higher_salary(self):
        """Получение вакансий с наибольшей зарплатой"""
        self.cur.execute("""
            SELECT com.name, vac.name, vac.salary_from
            FROM vacancies vac
            LEFT JOIN companies com USING(company_id)
            WHERE salary_from >= (
                SELECT AVG(salary_from)
                FROM vacancies
                WHERE salary_from IS NOT NULL)
        """)
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        """Получение вакансий по ключевому слову"""
        self.cur.execute(
            """
            SELECT com.name, vac.name, vac.salary_from
            FROM vacancies vac
            INNER JOIN companies com USING(company_id)
            WHERE LOWER(vac.name) LIKE LOWER(%s)""",
            (f"%{keyword}%",),
        )
        return self.cur.fetchall()

    def close(self):
        """Закрытие курсора и соединения"""
        self.cur.close()
        self.conn.close()
