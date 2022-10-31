from .base import Base
import os
from dotenv import load_dotenv
from binance.client import Client
from cpanel import models
import time
from django.utils import timezone
import threading

load_dotenv()

BET_TYPE = {
    "safe": {"bear": 2.4, "bull": 1.8},
    "gamble": {"bear": 3.0, "bull": 1.4},
    "insane": {"bear": 4.0, "bull": 1.0},
}
hash = []


class Predict:
    @staticmethod
    def make_number_equal(value1, value2):
        if value1 > value2:
            bigger_number = value1
            lower_number = value2
            wallet_name = 1
        else:
            bigger_number = value2
            lower_number = value1
            wallet_name = 2
        number_difference = bigger_number - lower_number
        divide_number = number_difference / 2
        # send divide_Number from bigger wallet to smaller wallet
        return [divide_number, wallet_name]

    @staticmethod
    def convert(amount, type="USD"):
        client = Client(os.getenv("APIKEY"), os.getenv("APISECRET"), tld="us")
        value = client.get_symbol_ticker(symbol="BNBUSD")["price"]
        usd_bnb = float("{:.6f}".format(float(amount) / float(value)))

        if type == "USD":
            return float("{:.2f}".format(float(value) * float(amount)))
        else:
            return usd_bnb

    @staticmethod
    def loked_true(data, current_epock):
        for index, value in enumerate(data, start=1):
            # check if balance is claimable meaning (if we won)
            if value.claimable(current_epock, value.current_address):
                models.pancakeswapPredicition.objects.filter(
                    epoch=current_epock, wallet_number=index
                ).update(claimable=True)

                # try to claime what we won
                try:
                    value.claim_wining(current_epock)
                except Exception as e:
                    Predict.write_file(
                        f"Error: {e} claiming wining failed wallet {index} won \n"
                    )
                else:
                    models.pancakeswapPredicition.objects.filter(
                        epoch=current_epock, wallet_number=index
                    ).update(claimed=True)

            return False

    @staticmethod
    def loked_false(data: list, bet_type: str, amount_in_bnb: float):
        seaching_for_bet = data[0].look_for_trade()
        seconds = seaching_for_bet[0]
        bull = seaching_for_bet[1]
        bear = seaching_for_bet[2]
        current_epock = data[0].current_epoch

        # check if how much time left
        if int(seconds) >= 15:
            Predict.write_file(f" waiting for {seconds - 20} seconds \n")
            time.sleep(seconds - 15)

        # time is less than 15 seconds prepare for bet
        bettype = BET_TYPE[bet_type]

        if int(seconds) <= 7:

            if (
                bull >= bettype["bull"]
                and bear >= bettype["bear"]
                or bear >= bettype["bull"]
                and bull >= bettype["bear"]
            ):
                save_data = [
                    data,
                    amount_in_bnb,
                    ["bear", "bull"],
                    current_epock,
                ]
                Predict.thread(save_data)
                hash_one = (
                    models.transaction_hash.objects.filter(
                        epoch=current_epock, wallet_number=1
                    )
                    .first()
                    .transaction_hash
                )
                hash_two = (
                    models.transaction_hash.objects.filter(
                        epoch=current_epock, wallet_number=2
                    )
                    .first()
                    .transaction_hash
                )

                data1 = {
                    "epoch": current_epock,
                    "bear": bear,
                    "bull": bull,
                    "wallet_number": 1,
                    "transaction_hash": hash_one,
                    "claimable": False,
                    "claimed": False,
                    "wallet_balance": data[0].wallet_balance(),
                    "bet_type": bet_type,
                }
                data2 = {
                    "epoch": current_epock,
                    "bear": bear,
                    "bull": bull,
                    "wallet_number": 2,
                    "transaction_hash": hash_two,
                    "claimable": False,
                    "claimed": False,
                    "wallet_balance": data[0].wallet_balance(),
                    "bet_type": bet_type,
                }

                data = [data1, data2]
                for i in data:
                    models.pancakeswapPredicition.objects.create(**i)

                # current_epock = data[0].current_epoch
                locked = True
                return [locked, current_epock]

            else:
                Predict.write_file(
                    f"Odds Not Profitable {seconds}  bull: {bull}, bear {bear} {bettype} \n"
                )

    def write_file(message):
        messages = f"{timezone.now()}: {message}"
        with open("predictions.txt", "a") as file:
            file.write(messages)
        models.message_logging.objects.create(message=messages)

    def thread(data):
        threads = list()
        for index, value in enumerate(data[0], start=0):
            x = threading.Thread(
                target=Predict.send_t,
                args=(value, data[1], data[2][index], data[3], index),
            )
            threads.append(x)
            x.start()

        for i in threads:
            i.join()

    def send_t(initilized_object, amount, type, epoch, wallet):
        try:

            result = initilized_object.send_transaction(amount, type)
            models.transaction_hash.objects.create(
                epoch=epoch, transaction_hash=result, wallet_number=wallet + 1
            )
        except Exception as e:
            Predict.write_file(f"Error: {e} \n")
