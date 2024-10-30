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
import json
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime

class ActionGetThongTinCuocGoi(Action):
    def name(self) -> Text:
        return "action_get_thong_tin_cuoc_goi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        conn = psycopg2.connect(
            dbname="rasa",
            user="poptech",
            password="metqu@D1",
            host="10.120.80.61",
            port="30011"
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * from conversation_info where sender_id = %s LIMIT 1",
            (tracker.sender_id,)
        )
        record = cursor.fetchone()
        if record is None:
            cursor.execute(
                "SELECT * from conversation_info order by RANDOM() LIMIT 1",
                (tracker.sender_id,)
            )
        record = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        #sender_id = "0"
        customer_title = "anh"
        customer_name = "Nam"
        customer_debt_due_date = datetime.now().strftime("%d/%m/%Y")
        customer_debt_amount = "0"
        if record is not None:
            #sender_id = record[0]
            customer_title = record[1]
            customer_name = record[2]
            customer_debt_due_date = record[3]
            customer_debt_amount = record[4]
        
        return [
            SlotSet("slot_customer_title", customer_title),
            SlotSet("slot_customer_name", customer_name),
            SlotSet("slot_customer_debt_due_date", customer_debt_due_date),
            SlotSet("slot_customer_debt_amount", customer_debt_amount)
        ]

class ActionSetSlotLyDoKhachHangKhongTraNo(Action):
    def name(self) -> Text:
        return "action_set_slot_ly_do_khach_hang_khong_tra_no"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_message = tracker.latest_message.get('text')
        return [SlotSet("slot_ly_do_khach_hang_khong_tra_no", last_message)]

class ActionCheckKHXinGiaHanNo(Action):
    def name(self) -> Text:
        return "action_check_kh_xin_gia_han_ngay_tra_no"

    def check_and_convert_date(self, date_string: str) -> datetime:
        pattern = r"^\d{1,2}/\d{1,2}/\d{4}$"
        if re.match(pattern, date_string):
            try:
                return datetime.strptime(date_string, "%d/%m/%Y")
            except ValueError:
                return None
        else:
            if date_string.isdigit():
                day = int(date_string)
                current_date = datetime.now()
                current_year = current_date.year
                current_month = current_date.month
                try:
                    return datetime(current_year, current_month, day)
                except:
                    return None
            return None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        kh_xin = tracker.get_slot("slot_xin_gia_han_ngay_tra_no")
        date = self.check_and_convert_date(kh_xin)
        try:
            ngay_hop_dong = datetime.strptime(tracker.get_slot("slot_customer_debt_due_date"), "%d/%m/%Y")
        except:
            return [
                SlotSet("slot_xin_gia_han_ngay_tra_no__status", "tre_hoac_khong_xd"),
                dispatcher.utter_message(response = "utter_tu_choi_han_ngay_tra_no")
            ]
        if date is None:
            return [
                SlotSet("slot_xin_gia_han_ngay_tra_no__status", "tre_hoac_khong_xd"),
                dispatcher.utter_message(response = "utter_tu_choi_han_ngay_tra_no")
            ]
        today = datetime.now().today()
        if date > ngay_hop_dong or date <= today:
            return [
                SlotSet("slot_xin_gia_han_ngay_tra_no__status", "tre_hoac_khong_xd"),
                SlotSet("slot_xin_gia_han_ngay_tra_no", date.strftime("%d/%m/%Y")),
                dispatcher.utter_message(response = "utter_tu_choi_han_ngay_tra_no")
            ]
        if date == ngay_hop_dong:
            return [
                SlotSet("slot_xin_gia_han_ngay_tra_no__status", "cung_ngay"),
                SlotSet("slot_xin_gia_han_ngay_tra_no", date.strftime("%d/%m/%Y"))
            ]
        return [
            SlotSet("slot_xin_gia_han_ngay_tra_no__status", "som"),
            SlotSet("slot_xin_gia_han_ngay_tra_no", date.strftime("%d/%m/%Y"))
        ]

class SubmitConversation(Action):
    def name(self) -> Text:
        return "action_submit_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
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
            (json_string,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        slot_xin_gia_han_ngay_tra_no__status = tracker.get_slot("slot_xin_gia_han_ngay_tra_no__status")
        slot_customer_debt_due_date = tracker.get_slot("slot_customer_debt_due_date")
        slot_customer_debt_amount = tracker.get_slot("slot_customer_debt_amount")
        slot_xin_gia_han_ngay_tra_no = tracker.get_slot("slot_xin_gia_han_ngay_tra_no")
        if slot_xin_gia_han_ngay_tra_no__status == "som":
            return [dispatcher.utter_message(text = f"Thông tin thanh toán: \n Số tiền thanh toán: {slot_customer_debt_amount}\n Ngày yêu cầu thanh toán: {slot_customer_debt_due_date}\n Ngày thanh toán: {slot_xin_gia_han_ngay_tra_no}")]
        return [dispatcher.utter_message(text = f"Thông tin thanh toán: \n Số tiền thanh toán: {slot_customer_debt_amount}\n Ngày yêu cầu thanh toán: {slot_customer_debt_due_date}\n Ngày thanh toán: {slot_customer_debt_due_date}")]
