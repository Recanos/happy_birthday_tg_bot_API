<<<<<<< HEAD
import requests
import json


class API:
    def __init__(self):
        self.BASE_URL = 'http://45.141.103.108:8000'

    def create_user(self, name, telegram_id, date_of_birth):
        requests.post(
            f"{self.BASE_URL}/employees/",
            json={
                "name": name,
                "telegram_id": telegram_id,
                "date_of_birth": date_of_birth
            }
        )

    def get_all_users(self):
        result = requests.get(
            f"{self.BASE_URL}/get_employees",
            params={"limit": 100, "skip": 0}
        ).json()

        name_ids = [[i["name"], i["telegram_id"]] for i in result]

        return name_ids

    def subscribe_on_user(self, user_id, subscribe_to_id):
        requests.post(
            f"{self.BASE_URL}/subscribe/{subscribe_to_id}",
            data=str(user_id)
        )

    def unsubscribe_on_user(self, user_id, unsubscribe_to_id):
        requests.delete(
            f"{self.BASE_URL}/unsubscribe/{unsubscribe_to_id}",
            data=str(user_id)
        )

    def subscribe_all(self, user_id):
        requests.post(
            f"{self.BASE_URL}/subscribe_all",
            data=str(user_id)
        )

    def unsubscribe_all(self, user_id):
        requests.delete(
            f"{self.BASE_URL}/unsubscribe_all",
            data=str(user_id)
        )

    def check_happy_birthday(self):
        birthday = requests.get(
            f"{self.BASE_URL}/check_happy_birthday"
        ).json()

        return birthday

    def get_employe_subs(self, telegram_id):
        employee = requests.get(
            f"{self.BASE_URL}/employee/{telegram_id}"
        ).json()

        employee_subs = employee["subscriptions"]
        result = []
        for subs in employee_subs:
            result.append(
                [
                    requests.get(
                        f"""{self.BASE_URL}/employee/{subs["subscribed_to_id"]}"""
                    ).json()["name"],
                    subs["subscribed_to_id"]

                ]
            )

        return result



=======
import requests
import json


class API:
    def __init__(self):
        self.BASE_URL = 'http://45.141.103.108:8000'

    def create_user(self, name, telegram_id, date_of_birth):
        requests.post(
            f"{self.BASE_URL}/employees/",
            json={
                "name": name,
                "telegram_id": telegram_id,
                "date_of_birth": date_of_birth
            }
        )

    def get_all_users(self):
        result = requests.get(
            f"{self.BASE_URL}/get_employees",
            params={"limit": 100, "skip": 0}
        ).json()

        name_ids = [[i["name"], i["telegram_id"]] for i in result]

        return name_ids

    def subscribe_on_user(self, user_id, subscribe_to_id):
        requests.post(
            f"{self.BASE_URL}/subscribe/{subscribe_to_id}",
            data=str(user_id)
        )

    def unsubscribe_on_user(self, user_id, unsubscribe_to_id):
        requests.delete(
            f"{self.BASE_URL}/unsubscribe/{unsubscribe_to_id}",
            data=str(user_id)
        )

    def subscribe_all(self, user_id):
        requests.post(
            f"{self.BASE_URL}/subscribe_all",
            data=str(user_id)
        )

    def unsubscribe_all(self, user_id):
        requests.delete(
            f"{self.BASE_URL}/unsubscribe_all",
            data=str(user_id)
        )

    def check_happy_birthday(self):
        birthday = requests.get(
            f"{self.BASE_URL}/check_happy_birthday"
        ).json()

        return birthday

    def get_employe_subs(self, telegram_id):
        employee = requests.get(
            f"{self.BASE_URL}/employee/{telegram_id}"
        ).json()

        employee_subs = employee["subscriptions"]
        result = []
        for subs in employee_subs:
            result.append(
                [
                    requests.get(
                        f"""{self.BASE_URL}/employee/{subs["subscribed_to_id"]}"""
                    ).json()["name"],
                    subs["subscribed_to_id"]

                ]
            )

        return result



>>>>>>> 523e111b3b7e89f078dd8941e429c20216035a24
