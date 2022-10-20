# from ctypes import addressof
# from http import client
# from importlib.resources import path
# import symbol
# from typing import Type
from email import message
import logging
from django.http import HttpResponse
from django.shortcuts import render, redirect

# from django.contrib.auth.models import User
# from dashboard import models as dashboard_model
from . import forms, models
from django.contrib import messages
import random, os

# from django.utils import timezone
# from datetime import date, timedelta, datetime
# from dateutil.relativedelta import *
from binance.client import Client
from dotenv import load_dotenv
from src import base

# from src import main
import time
from django.utils import timezone
import threading
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


BET_TYPE = {"safe": {"bear": 2.5, "bull": 1.8}, "gamble": {"bear": 3.0, "bull": 1.4}}
wallet_1 = [os.getenv("wallet_pk_one"), os.getenv("wallet_address_one")]
wallet_2 = [os.getenv("wallet_pk_two"), os.getenv("wallet_address_two")]

# Create your views here.
load_dotenv()

hash = []
threading_ = []
locked = False
current_epock = 0


@login_required(login_url="/login")
def cpanel(request):
    wallet_one_balance = initialize(wallet_1).wallet_balance()
    wallet_two_balance = initialize(wallet_2).wallet_balance()
    server = models.server_status.objects.all().order_by("-created_at").first()
    total_bet = models.pancakeswapPredicition.objects.all().count()
    total_success = models.pancakeswapPredicition.objects.filter(claimable=True).count()
    context = {
        "sub_title": "webcome back ",
        "wallet_one": convert(wallet_one_balance, "USD"),
        "wallet_two": convert(wallet_two_balance, "USD"),
        "server": server,
        "total_bet": total_bet,
        "total_success": total_success,
    }
    return render(request, "cpanel/cpanel.html", context)


def initialize(wallets):
    path = os.getcwd() + "/src/abi/abi.json"
    return base.Base(wallets[1], wallets[0], path)


def main(request):
    bet_type = request.POST["bet_type"]
    balance = request.POST["balance"]
    amount_in_bnb = convert(balance, type="BNB")

    waiting_time_to_claime = 310  # > 5 minutes

    while True:

        prediction_1 = initialize(wallet_1)
        prediction_2 = initialize(wallet_2)

        if locked:
            lock_true(
                waiting_time_to_claime, [prediction_1, prediction_2], current_epock
            )
        else:
            locked_false([prediction_1, prediction_2], bet_type, amount_in_bnb)

        time.sleep(1)


def start(request):
    if request.POST:
        y = threading.Thread(target=main, args=(request,), daemon=True)
        global threading_
        y.start()
        threading_.append(y)

        # y.join()

        models.server_status.objects.create(
            status=True,
            logging="Running",
            started_at=timezone.now(),
            stoped_at=None,
            updated_at=None,
        )

    return HttpResponse("running...")


# when the bet is placed
def lock_true(waiting_time, initialize_object, current_epoch):
    write_file("waiting for 5 minutes Before Checking for result \n")

    time.sleep(waiting_time)
    wallet_balance_one = initialize_object[0].wallet_balance()
    wallet_balance_tow = initialize_object[1].wallet_balance()
    # convert balance from wallet one to wallet to to be equal

    difference = make_number_equal(
        float(convert(wallet_balance_one, "USD")),
        float(convert(wallet_balance_tow, "USD")),
    )
    amount_in_bnb = convert(difference[0], "BNB")

    if difference[1] == "wallet1":
        # send money from wallet one to wallet two
        try:
            tx = initialize_object[0].send(
                amount_in_bnb, initialize_object[1].account_address
            )
            write_file(
                f"Sent {amount_in_bnb} BNB from wallet1 to wallet 2  hash {tx} \n"
            )
        except Exception as e:
            write_file(f"Failed to send {amount_in_bnb} BNB to Wallet 2 |Error: {e} \n")

    else:
        # send money from wallet two to wallet one
        try:

            tx = initialize_object[1].send(
                amount_in_bnb, initialize_object[0].account_address
            )
            write_file(
                f"Sent {amount_in_bnb} BNB from wallet2 to wallet 1 hash {tx} \n"
            )
        except Exception as e:
            write_file(f"Failed to send {amount_in_bnb} BNB to wallet 1 | Error : {e}")

    # try to see how much we made
    claimable1 = initialize_object[0].claimable(
        current_epoch, initialize_object[0].current_address
    )
    claimable2 = initialize_object[1].claimable(
        current_epoch, initialize_object[1].current_address
    )

    if claimable1:
        models.pancakeswapPredicition.objects.filter(
            epoch=current_epoch, wallet_number=1
        ).update(claimable=True)
    elif claimable2:
        models.pancakeswapPredicition.objects.filter(
            epoch=current_epoch, wallet_number=2
        ).update(claimable=True)
    else:
        message = f"Transaction failed : Not bettable or insuficient fund , epoch :{current_epoch} \n"
        write_file(message)
        models.server_status.objects.create(
            status=True, logging=message, updated_at=timezone.now()
        )
    global locked
    locked = False

    return locked


# not in bet looking for bet


def locked_false(initialized_pbjects, bet_type, amount_in_bnb):
    looking = initialized_pbjects[0].look_for_trade()
    seconds = looking[0]
    bull = float(looking[1])
    bear = float(looking[2])

    if int(seconds) >= 15:
        write_file(f"{timezone.now()}:  print waiting for {seconds - 20} seconds \n")
        time.sleep(seconds - 15)

    if seconds <= 15:
        trade_type = BET_TYPE[bet_type]

        if (
            (bull >= trade_type["bull"])
            and (bear >= trade_type["bear"])
            or (bear >= trade_type["bear"])
            and (bull >= trade_type["bull"])
        ):

            data = [
                initialized_pbjects,
                amount_in_bnb,
                ["bear", "bull"],
                "send_transation",
            ]

            try:
                thread(data)
            except Exception as e:
                write_file(f"Error: {e}")
            data1 = {
                "epock": initialized_pbjects[0].current_epoch,
                "bear": bear,
                "bull": bull,
                "wallet_number": 1,
                "transaction_hash": hash[0],
                "claimable": False,
                "claimed": False,
                "wallet_balance": initialized_pbjects[0].wallet_balance(),
                "bet_type": bet_type,
            }
            data2 = {
                "epock": initialized_pbjects[1].current_epoch,
                "bear": bear,
                "bull": bull,
                "wallet_number": 2,
                "transaction_hash": hash[2],
                "claimable": False,
                "claimed": False,
                "wallet_balance": initialized_pbjects[0].wallet_balance(),
                "bet_type": bet_type,
            }
            data = [data1, data2]
            _save(data)
            global current_epock
            current_epock = initialized_pbjects[0].current_epoch
            global locked
            locked = True
            return locked
        else:
            write_file(
                f"{timezone.now()}: Bull({bull}), bear({bear}) Not profitable odds \n"
            )
            return
    else:
        write_file(
            f"{timezone.now()} : Current epock{initialized_pbjects[0].current_epoch} expired |  seconds {seconds} | Bull {bull} | bear {bear} \n"
        )
        return


def send_transaction(initilized_object, amount, type):
    global hash
    result = initilized_object.send_transaction(amount, type)
    hash.append(result)


def convert(amount, type="USD"):
    client = Client(os.getenv("APIKEY"), os.getenv("APISECRET"), tld="us")
    value = client.get_symbol_ticker(symbol="BNBUSD")["price"]
    usd_bnb = float("{:.6f}".format(float(amount) / float(value)))

    if type == "USD":
        return float("{:.2f}".format(float(value) * float(amount)))
    else:
        return usd_bnb


def thread(data):
    threads = list()
    for index, value in enumerate(data[0], start=0):
        x = threading.Thread(
            target=send_transaction, args=(value, data[1], data[index])
        )
        threads.append(x)
        x.start()

    for i in threads:
        i.join()


def write_file(message):
    with open("predictions.txt", "a") as file:
        file.write(message)
    models.message_logging.objects.create(message=message)


# make two different number equal
def make_number_equal(value1, value2):
    if value1 > value2:
        bigger_number = value1
        lower_number = value2
        wallet_name = "wallet2"
    else:
        bigger_number = value2
        lower_number = value1
        wallet_name = "wallet1"
    number_difference = bigger_number - lower_number
    divide_number = number_difference / 2
    # send divide_Number from bigger wallet to smaller wallet
    return [divide_number, wallet_name]


def _save(data):
    for i in data:
        models.pancakeswapPredicition.objects.create(**i)


@csrf_exempt
def fetchlogs(request):
    if request.POST:
        if threading_:
            for i in threading_:
                if i.is_alive():
                    return HttpResponse("Thread still running")
                else:
                    server_ = models.server_status.objects.filter(
                        status=True
                    ).update_or_create(
                        status=False,
                        logging="THreading is not running",
                    )
                    return HttpResponse("down")
        else:
            server_ = models.server_status.objects.filter(status=True).update_or_create(
                status=False,
                logging="THreading is not running",
            )
            return HttpResponse("down")


@csrf_exempt
def showlogs(request):
    if request.POST:
        data = models.message_logging.objects.latest("created_at")
        print(data.message)
        return HttpResponse(data.message)


@csrf_exempt
def clearlogs(request):
    if request.POST:
        models.message_logging.objects.all().delete()
