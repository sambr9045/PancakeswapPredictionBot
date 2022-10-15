import time
from src import base
import os
from dotenv import load_dotenv
from src import db
from datetime import datetime
import random
import  uuid

load_dotenv()

locked = False


def main(database_connection):
    global locked
    AMOUNT_TO_TRADE = 0.01
    wallet_1 = [os.getenv('wallet_pk_one'), os.getenv("wallet_address_one")]
    wallet_2 = [os.getenv('wallet_pk_two'), os.getenv("wallet_address_two")]
    prediction = initiation(wallet_1[1], wallet_1[0])
    prediction2 = initiation(wallet_2[1], wallet_2[0])
    prediction_message = ""
    current_epock = 0
    waiting_time_after_bet = 310

    if locked:

        print("sleeping for 3 minutes . Before checking for result.. ")

        time.sleep(waiting_time_after_bet)
        print("Checking for result ")
        wallet_balance_one = prediction.wallet_balance()
        wallet_balance_two = prediction2.wallet_balance()
        print(wallet_balance_two, wallet_balance_one)

        difference = make_number_equal(float(wallet_balance_one), float(wallet_balance_two))
        if difference[1] == "wallet1":
            result = prediction.send(difference[0], prediction.account_address)
            print("wallet")
        else:
           result = prediction2.send(difference[0], prediction2.account_address)
            print("wallet2")
        write_file(f"Send money from one account to different account {result}")

        claimable1 = prediction.claimable(current_epock, prediction.account_address)
        claimable2 = prediction2.claimable(current_epock, prediction2.account_address)

        if claimable1:
            # update databse set wallet one to true wallet two to false
            qeury1 = f""" UPDATE BET 
            SET claimable = 'True' WHERE epoch = '{current_epock}' and wallet_number = '1'
            """
            database_connection[0].execute_query(database_connection[1], qeury1)

        elif claimable2:
            # update database set wallet two to true and wallet one to false
            qeury2 = f""" UPDATE BET 
             SET claimable = 'True' WHERE epoch = '{current_epock}' and wallet_number = '2'
            """
            database_connection[0].execute_query(database_connection[1], qeury2)

        else:
            write_file(f"Transaction Failed both predition1 {claimable1} and prediciton2 {claimable2} are false \n")

        locked = False

    else:
        # look for trade
        print("start looking for bet... ")
        looking = prediction.look_for_trade()
        seconds = looking[0]
        bull = float(looking[1])
        bear = float(looking[2])

        if seconds >= 20:
            print(f"print waiting for {seconds} seconds")
            time.sleep(seconds-20)

        if seconds <= 10:
            if ((bull >= 1.0) and (bear >= 2.0)) or ((bull >= 2.0) and (bear >= 1.0)):
                # placing bet
                tx_pk1 = prediction.send_transaction(AMOUNT_TO_TRADE, 'bear')
                tx_pk2 = prediction2.send_transaction(AMOUNT_TO_TRADE, 'bull')

                # collecting data
                data1 = [prediction.current_epoch, bear, bull, 1, tx_pk1, False, datetime.now()]
                data2 = [prediction2.current_epoch, bear, bull, 2, tx_pk2, False, datetime.now()]
                # saving data
                save(data1, database_connection)
                save(data2, database_connection)
                current_epock = prediction.current_epoch
                locked = True
            else:
                message = f" bull , bear not in market {bull, bear}"
                return message
        else:
            message = f"Seconde: {seconds}, Bull {bull}, Bear {bear} \n"
            return message

    # save prediction massege in dot text file
    write_file(prediction_message)


def save(data, database):
    QUERY = f"""
    INSERT INTO BET VALUES ('{data[0]}', '{data[1]}', '{data[2]}',  '{str(data[3])}',  '{data[4]}', '{data[5]}', '{str(data[6])}');
    """
    database[0].execute_query(database[1], QUERY)
    return True


def initiation(pk, address):
    path = os.getcwd() + "/src/abi/abi.json"
    pancake = base.Base(pk, address, path)
    return pancake


def write_file(message):
    with open("predictions.txt", "a") as file:
        file.write(message)

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


def connection():
    db_connection = db.DB("localhost", "root", "", "pancakeswapprediction")
    connection = db_connection.db_connector()
    return [db_connection, connection]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dbconnection = connection()
    # s = initiation(os.getenv("wallet_address_one"), os.getenv('wallet_pk_one'))
    # # print(s.claimable(112003, os.getenv("wallet_address_two")))
    # # print(s.account_address)
    # # o = s.claim_wining(112003)
    # print(s.wallet_balance())
    while True:
        response = main(dbconnection)
        print(response)
        print()
        time.sleep(2)
