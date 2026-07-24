from kungfu_chess.events.messages.move_requested_message import MoveRequestedMessage
from kungfu_chess.model.position import Position


def main():

    player_id = "player1"

    print(
        f"Client started: {player_id}"
    )

    message = MoveRequestedMessage(
        source=Position(0,0),
        destination=Position(0,1),
    )

    print("Sending move:", message)


if __name__ == "__main__":
    main()