def format_phone_number(number):
    if len(number) == 13:
        if number.startswith("234"):
            return number
    elif len(number) == 11:
        if number.startswith("0"):
            return number.replace("0", "234", 1)
    elif len(number) == 10:
        return "234" + number
    return None
