import time
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re


#  python3 -m uvicorn main:app --reload
app = FastAPI()

subscription_bank = {
    'netflix_standard': {'path': 'https://help.netflix.com/en/node/24926','phrase': 'Standard with ads:'},
    'hulu_no_ads': {'path': 'https://www.hulu.com/no-ads','phrase': 'Standard with ads:'}
}

class Subscriptions(BaseModel):
    id: str
    current_price: float
    

@app.post("/check-prices")
def receive_subscriptions(subscriptions: list[Subscriptions]):
    """
    Receives a message, prints it, and returns a confirmation response.
    """

    print("Received message:", subscriptions)

    updated_list = []
    

    for sub in subscriptions:
        new_price = check_price(sub.id)
        if new_price != sub.current_price:
            
            updated_price = { "id": sub.id,
                              "new_price": check_price(sub.id),
                              "old_price": sub.current_price
                            }

            updated_list.append(updated_price)
            print('NEW PRICE:', updated_list)
    
    message_payload = {"changed_subscriptions" : updated_list}

    try:
        print(f"Sending message: '{message_payload}'")
        
        # Send a POST request with the JSON payload
        return message_payload

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")




def check_price(subscription_name):

    
    url = subscription_bank[subscription_name]['path']

    response = requests.get(url)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')

        text = soup.get_text()

        pattern = r"\$(\d+\.\d+)"
        match = re.search(pattern, text)

        if match:
            price_str = match.group(1)
            price_float = float(price_str)
            print(f"Found price: {price_float}")
            return price_float
        else:

            print("Price not found.")

    else:
        print(f"Failed to retrieve page. Status code: {response.status_code}")

