import requests
from bs4 import BeautifulSoup
import smtplib
import json


def read_amazon(url=""):
    head = {
        "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
    }
    response = requests.get(url, headers=head)
    ms_site = response.text

    soup = BeautifulSoup(ms_site, features="lxml")

    price = soup.find(name="span", class_="a-price a-text-price a-size-medium apexPriceToPay").getText()

    price_raw = float(price.split("$")[1])

    return soup.find(id="productTitle").get_text().strip(), price_raw


def send_notification_email(product_name="", product_price=0.0, product_url=""):
    # --------- Params Load -------------- #
    with open("connection.json") as json_file:
        connection_params = json.load(json_file)

    my_mail = connection_params["from_email"]
    password = connection_params["password"]
    smtp_server = connection_params["smtp_server"]
    port = connection_params["smtp_port"]
    to_mail = connection_params["to_email"]
    product_name = product_name.encode("utf-8").strip()

    subject = "Amazon Price Alert!"
    message = f"The product which you were observing: {product_name}\n" \
              f"is in a good price: {product_price}\n" \
              f"Check this link: {product_url}"

    try:
        with smtplib.SMTP(smtp_server, port, timeout=120) as connection:
            connection.starttls()
            connection.login(user=my_mail, password=password)
            connection.sendmail(
                from_addr=my_mail,
                to_addrs=to_mail,
                msg=f"Subject:{subject}"
                    f"\n\n{message}")
    except smtplib.SMTPServerDisconnected:
        print("Email not sent, smtp problem")


if __name__ == '__main__':

    url = "https://www.amazon.com/Instant-Pot-Plus-Programmable-Sterilizer/dp/B01NBKTPTS?th=1"

    title, price = read_amazon(url)

    threshold = 100

    if price < threshold:
        send_notification_email(title, price, url)
