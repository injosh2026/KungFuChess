from img import Img
from kungfu_chess.ui.composition_root import build_app


def main() -> None:
    build_app(Img()).run()


if __name__ == "__main__":
    main()
