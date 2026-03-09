

import requests

import time


class APIhh:
    """Класс для работы с сайтом API hh.ru"""
    def __init__(self):
        self.base_url = "https://api.hh.ru"
        self.headers = {"User-Agent": "hh_api_db/1.0"}

    def get_employers(self,employer_name: list[str]) -> list[dict[str, str]]:
        """Получение данных работодателя"""
        employers_data = []
        for name in employer_name:
            params = {
                "text": name,
                "only_with_vacancies": True,
                "type": "company",
                "area": 113
            }
            response = requests.get(
                f"{self.base_url}/employers", params=params, headers=self.headers
            )
            if response.status_code == 200:
                items = response.json().get("items")
                if items:
                    employers_data.append(items[0])
            else:
                print(status_code)

            time.sleep(0.2)

        return employers_data


    def get_vacancies(self, employer_id: str) -> list[dict[str, str]]:
        """Получение данных о вакансиях по работодателю"""
        params = {
            "employer_id": employer_id,
            "per_page": 30
        }
        response = requests.get(
            f"{self.base_url}/vacancies", params=params, headers=self.headers
        )
        if response.status_code == 200:
            return response.json().get("items", [])

        return []
