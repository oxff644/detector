import logging

from termcolor import colored

from config import Config

logging.basicConfig(format="[%(asctime)s] %(message)s", level=logging.INFO)
loger = logging.getLogger(Config.name)


def base_msg(txt, color, tag="[-]"):
    loger.info(f"{tag}{colored(txt, color)}")


def info(txt):
    base_msg(txt, "blue", "[*]")


def success(txt):
    base_msg(txt, "green", "[+]")


def warning(txt):
    base_msg(txt, "yellow", "[=]")


def error(txt):
    base_msg(txt, "red", "[x]")


if __name__ == "__main__":
    info("blue")
    success("green")
    warning("yellow")
    error("red")
