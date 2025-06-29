import os
import datetime

def is_expired(expiry_date_str):
    """
    expiry_date_str = format: 'YYYY-MM-DD'
    Returns True if expired, else False
    """
    today = datetime.date.today()
    expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
    return today > expiry_date


def get_expiry_date():
    """
    Reads expiry date from expiry.txt file
    """
    if not os.path.exists("expiry.txt"):
        return None
    with open("expiry.txt", "r") as f:
        return f.read().strip()


def save_expiry_date(new_expiry_date):
    """
    Saves new expiry date to expiry.txt
    """
    with open("expiry.txt", "w") as f:
        f.write(new_expiry_date)
