import time
from src import base
import os
from dotenv import load_dotenv

load_dotenv()
locked = False


def main():
    global locked
    AMOUNT_TO_TRADE = 0.01
    wallet_1 = [os.getenv('wallet_pk_one'), os.getenv("wallet_address_one")]
    wallet_2 = [os.getenv('wallet_pk_two'), os.getenv("wallet_address_two")]
    prediction = initiation(wallet_1[1], wallet_1[0])
    prediction2 = initiation(wallet_2[1], wallet_2[0])
    prediction_message = ""
    in_position = []

    if locked:
        # wallet_1
        # prediction = initiation(wallet_1[1], wallet_1[0])
        # prediction2 = initiation(wallet_2[1], wallet_2[0])
        if prediction.claimable(in_position[0], in_position[1]):
            prediction.claim_wining(in_position[0])
            locked = True
            prediction_message = f"wallet one monie claime"

        else:
            print(f"claimable fable wallet 1 code {prediction.current_epoch}")

        if prediction2.claimable(in_position[0], in_position[2]):
            prediction2.claim_wining(in_position)
            locked = True
            prediction_message = f"wallet two monie claime"
        else:
            print(f"claimable fable wallet 2 code {prediction2.current_epoch}")
            time.sleep(5)
    else:
        # look for trade
        looking = prediction.look_for_trade()
        seconds = looking[0]
        bull = float(looking[1])
        bear = float(looking[2])

        if seconds >= 20:
            print(f"print waiting for {seconds} seconds")
            time.sleep(seconds-20)

        if seconds <= 10:
            if ((bull >= 1.4) and (bear >= 2.4)) or ((bull >= 2.4) and (bear >= 1.4)):
                prediction.send_transaction(AMOUNT_TO_TRADE, 'bear')
                # sending second wallet
                prediction2.send_transaction(AMOUNT_TO_TRADE, 'bull')
                locked = True

                print(f" {seconds} in position order placed Bull{bull}, Bear {bear}")
                in_position.append(prediction.current_epoch)
                in_position.append(prediction.account_address)
                in_position.append(prediction2.account_address)
                locked = True
            else:
                message = f"bull , bear not in market {bull, bear}"
                return message
        else:
            message = f"Seconde: {seconds}, Bull {bull}, Bear {bear} \n"
            return message
    write_file(prediction_message)


def initiation(pk, address):
    path = os.getcwd() + "/src/abi/abi.json"
    pancake = base.Base(pk, address, path)
    return pancake


def write_file(message):
    with open("predictions.txt", "a") as file:
        file.write(message)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # s = initiation(os.getenv("wallet_address_one"), os.getenv('wallet_pk_one'))
    # print(s.claimable(112003, os.getenv("wallet_address_two")))
    # print(s.account_address)
    # o = s.claim_wining(112003)
    # print(o)
    while True:
        response = main()
        print(response)
        print()
        time.sleep(2)
