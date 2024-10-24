# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import psycopg2
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionSetSlotLyDoKhachHangKhongTraNo(Action):
    def name(self) -> Text:
        return "action_set_slot_ly_do_khach_hang_khong_tra_no"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_set_slot_ly_do_khach_hang_khong_tra_no...")
        last_message = tracker.latest_message.get('text')
        return [SlotSet("slot_ly_do_khach_hang_khong_tra_no", last_message)]

class SubmitConversation(Action):
    def name(self) -> Text:
        return "action_submit_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_submit_conversation...")
        json_object = {
            "sender_id": tracker.sender_id,
            "slot_receiver_name": tracker.get_slot("slot_receiver_name"),
            "slot_ly_do_khach_hang_khong_tra_no": tracker.get_slot("slot_ly_do_khach_hang_khong_tra_no"),
            "slot_xin_gia_han_ngay_tra_no": tracker.get_slot("slot_xin_gia_han_ngay_tra_no")
        }
        json_string = json.dumps(json_object)
        conn = psycopg2.connect(
            dbname="rasa",
            user="poptech",
            password="metqu@D1",
            host="10.120.80.61",
            port="30011"
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversation_submitted (data) VALUES (%s)",
            (json_string)
        )
        return []
