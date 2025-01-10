from datetime import datetime


def is_valid_date(date_string):
    try:
        # Try to parse the date string with the given format
        if date_string:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        else:
            return False
    except ValueError:
        # If a ValueError is raised, the string does not match the format
        return False