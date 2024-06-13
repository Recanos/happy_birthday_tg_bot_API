import requests
import json


class API:
    def __init__(self):
        self.BASE_URL = 'http://45.141.103.108:8000'

    def create_user(self, name, telegram_id, date_of_birth):
        requests.post(
            "http://45.141.103.108:8000/employees/",
            json={
                "name": name,
                "telegram_id": telegram_id,
                "date_of_birth": date_of_birth
            }
        )

    def get_all_users(self):
        result = requests.get(
            "http://45.141.103.108:8000/get_employees",
            params={"limit": 100, "skip": 0}
        ).json()

        name_ids = [[i["name"], i["telegram_id"]] for i in result]

        return name_ids

    def subscribe_on_user(self, user_id, subscribe_to_id):
        requests.post(
            f"http://45.141.103.108:8000/subscribe/{subscribe_to_id}",
            data=str(user_id)
        )

    def unsubscribe_on_user(self, user_id, unsubscribe_to_id):
        requests.delete(
            f"http://45.141.103.108:8000/unsubscribe/{unsubscribe_to_id}",
            data=str(user_id)
        )

    def subscribe_all(self, user_id):
        requests.post(
            "http://45.141.103.108:8000/subscribe_all",
            data=str(user_id)
        )

    def unsubscribe_all(self, user_id):
        requests.delete(
            "http://45.141.103.108:8000/unsubscribe_all",
            data=str(user_id)
        )

    def check_happy_birthday(self):
        birthday = requests.get(
            "http://45.141.103.108:8000/check_happy_birthday"
        ).json()

        return birthday

    def get_employe_subs(self, telegram_id):
        employee = requests.get(
            f"http://45.141.103.108:8000/employee/{telegram_id}"
        ).json()

        employee_subs = employee["subscriptions"]
        result = []
        for subs in employee_subs:
            result.append(
                [
                    requests.get(
                        f"""http://45.141.103.108:8000/employee/{subs["subscribed_to_id"]}"""
                    ).json()["name"],
                    subs["subscribed_to_id"]

                ]
            )

        return result


session = API()
print(session.get_employe_subs(2))
api = API()
users = api.get_all_users()
print(users.remove(session.get_employe_subs(2)[0]))
print(users)


