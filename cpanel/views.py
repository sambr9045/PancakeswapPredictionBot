from telnetlib import STATUS
from django.http import HttpResponse, JsonResponse
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
from src.predict import Predict

# from src import main
import time
from django.utils import timezone
import threading
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView


wallet_1 = [os.getenv("wallet_pk_one"), os.getenv("wallet_address_one")]
wallet_2 = [os.getenv("wallet_pk_two"), os.getenv("wallet_address_two")]

# Create your views here.
load_dotenv()

hash = []
first_thread = []
exite_thread = None
locked = False
current_epock = 0


@login_required(login_url="/login")
def cpanel(request):
    # wallet_one_balance = Bot.initialize(wallet_1).wallet_balance()
    # wallet_two_balance = Bot.initialize(wallet_2).wallet_balance()
    server = models.server_status.objects.all().order_by("-created_at").first()
    total_bet = models.pancakeswapPredicition.objects.all().count()
    total_success = models.pancakeswapPredicition.objects
    context = {
        "sub_title": "webcome back ",
        "server": server,
        "total_bet": total_bet,
        "total_success": total_success.filter(claimable=True).count(),
        "total_bet_row": total_success.all().order_by("-created_at")[0:10],
    }
    return render(request, "cpanel/cpanel.html", context)


class Bot(TemplateView):
    def __init__(self) -> None:
        self.wallet_object_one = self.initialize(wallet_1)
        self.wallet_object_two = self.initialize(wallet_2)
        self.locked = False
        self.bet_type = ""
        self.amount_in_bnb = 0
        self.waitin_time_to_claim = 310
        self.hash = []

        self.second_thread = []
        self.current_epoch = 0

    @staticmethod
    def initialize(wallets):
        path = os.getcwd() + "/src/abi/abi.json"
        return base.Base(wallets[1], wallets[0], path)

    def get(self, request, *args, **kwargs):

        if request.is_ajax:

            # fetch wallet balance
            if "load_balance" in request.GET:

                wallet_one_balance = self.initialize(wallet_1).wallet_balance()
                wallet_two_balance = self.initialize(wallet_2).wallet_balance()
                response = {
                    "wallet_one": Predict.convert(wallet_one_balance),
                    "wallet_two": Predict.convert(wallet_two_balance),
                }
                return JsonResponse(response)

            # clear logs in database
            if "clear_logs" in request.GET:
                models.message_logging.objects.all().delete()
                return JsonResponse({"result": "done"})

            # fetch server logs
            if "fetch_logs" in request.GET:
                data = (
                    models.message_logging.objects.all().order_by("-created_at").first()
                )

                if not data:
                    value = "server_off"
                else:
                    value = data.message
                return JsonResponse({"result": value})

    def post(self, request, *args, **kwargs):
        # starting bot thread
        server_status = models.server_status.objects

        if server_status.all().first().status == False:
            server_status.all().update(status=True)

        if request.is_ajax and "start_bot" in request.POST:
            try:
                global exite_thread
                exite_thread = True
                x = threading.Thread(target=self.bot, args=(request,))
                x.start()

                global first_thread
                first_thread.append(x)
                # models.thread_value.objects.create(x=x)
                return JsonResponse({"result": "Thread is running"})
            except Exception as e:
                server_status.all().update(status=False)
                Predict.write_file(f"Server Failed and error occured : Error {e}")

        # stabilized balance from dashboard
        if request.is_ajax and "stabilize_balance" in request.POST:
            result = self.stablized_balance()
            Predict.write_file(result)
            return JsonResponse({"result": result})

        # check thread status
        if request.is_ajax and "thread_running" in request.POST:
            # thead_id = models.thread_value.objects.all()
            if first_thread:
                for i in first_thread:
                    if i.is_alive():
                        return JsonResponse({"result": "Thread is running"})
                    else:
                        models.server_status.objects.all().update(
                            status=False, stoped_at=timezone.now()
                        )

                        return JsonResponse({"result": "down"})
            else:

                models.server_status.objects.all().update(
                    status=False, stoped_at=timezone.now()
                )
                return JsonResponse({"result": "down"})

        # stop thread
        if "stop_thread" in request.POST:
            exite_thread = False
            first_thread = []
            models.server_status.objects.all().update(
                status=False, started_at=timezone.now()
            )
            return JsonResponse({"result": "thread_stopped"})

    # STARTING PREDICTION BOT
    def bot(self, request):
        self.bet_type = request.POST["bet_type"]
        self.amount_in_bnb = Predict.convert(request.POST["balance"], type="BNB")

        while exite_thread:

            self.wallet_object_one = self.initialize(wallet_1)
            self.wallet_object_two = self.initialize(wallet_2)

            if self.locked:
                Predict.write_file(
                    f"But placed waiting  for 5 minutes before checking balance \n"
                )
                time.sleep(self.waitin_time_to_claim)
                result = self.stablized_balance()
                Predict.write_file(result)
                self.locked = Predict.loked_true(
                    [self.wallet_object_one, self.wallet_object_two], self.current_epoch
                )

            else:
                values = Predict.loked_false(
                    [self.wallet_object_one, self.wallet_object_two],
                    self.bet_type,
                    self.amount_in_bnb,
                )
                if values or values is not "":
                    self.current_epoch = values[1]
                    self.locked = values[0]

            time.sleep(1)

    # STABILIZED PRICE (make wallet1 and wallet 2 equal)
    def stablized_balance(self):
        balance_one = Predict.convert(self.wallet_object_one.wallet_balance())
        balance_two = Predict.convert(self.wallet_object_two.wallet_balance())
        vals = Predict.make_number_equal(balance_one, balance_two)
        new_value = []
        if vals[1] == 1:
            new_value.append(
                [self.wallet_object_one, self.wallet_object_two.account_address]
            )
        elif vals[1] == 2:
            new_value.append(
                [self.wallet_object_two, self.wallet_object_one.account_address]
            )

        try:
            new_value[0][0].send(Predict.convert(vals[0], "BNB"), new_value[0][1])

            return f"Wallet {vals[1]} sent ${vals[0]} to other wallet"

        except Exception as e:
            message = f"Stabilized wallet balance failed; Error: {e} {vals[0]}\n"
            return message
