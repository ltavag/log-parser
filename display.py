from colorama import Fore, Back, Style

FIELD_LENGTH = 50


def display_message(message):
    print(Fore.BLUE + message + Style.RESET_ALL)


def display_stats(stats):
    """
        Display one line with multiple key
        values that are justified to uniform 
        length
    """
    message = '\t' + Fore.BLUE
    for k, v in stats.items():
        message += '{}: {}'.format(k, v).ljust(FIELD_LENGTH, ' ')

    message += Style.RESET_ALL
    print(message)


def display_alert_triggered(message):
    print('\t' + Fore.RED + message + Style.RESET_ALL)


def display_alert_resolved(message):
    print('\t' + Fore.GREEN + message + Style.RESET_ALL)
