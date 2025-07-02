import fire

from speech2caret.main import main


def cli() -> None:
    fire.Fire(main)
