import colorama
from colorama import Fore, Style

def print_color(message, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{message}{Style.RESET_ALL}")