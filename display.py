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
    for stat_line in stats:
        message = '\t' + Fore.BLUE
        for k, v in stat_line.items():
            message += '{}: {}'.format(k, v).ljust(FIELD_LENGTH, ' ')

        message += Style.RESET_ALL
        print(message)


def display_alerts(triggered, resolved):
    for message in triggered:
        print(Fore.RED + message + Style.RESET_ALL)
    for message in resolved:
        print(Fore.GREEN + message + Style.RESET_ALL)
