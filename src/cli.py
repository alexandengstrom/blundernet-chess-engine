import argparse

from engine import Engine, Model, InfiniteDataset, Evaluator
from lichess_bot import LichessBot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train or manage the model.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train the model")
    train_parser.add_argument(
        "--name",
        type=str,
        default="null",
        help="Optional name for the training run",
    )

    train_parser.add_argument(
        "--generate_data",
        type=bool,
        default=False,
        help="Generate new training data while training",
    )

    lichess_parser = subparsers.add_parser("lichess", help="Host Lichess Bot")
    lichess_parser.add_argument(
        "--model", type=str, default="blundernet", help="Model to run in the engine"
    )
    lichess_parser.add_argument(
    "--stats", action="store_true", help="Show account statistics and exit"
    )

    game_parser = subparsers.add_parser("game", help="Play against the models via Pygame GUI")
    eval_parser = subparsers.add_parser("eval", help="Evaluate a model")
    eval_parser.add_argument(
        "--model", type=str, default="blundernet", help="Model to evaluate"
    )
    
    args = parser.parse_args()

    if args.command == "train":
        model = Model.load(args.name if args.name != "null" else None)
        dataset = InfiniteDataset(model)
        model.train(dataset)

    elif args.command == "lichess":
        model = args.model

        engine = Engine(Model.load(args.model))
        token = None # pylint: disable=invalid-name

        with open(".token", "r", encoding="utf-8") as data:
            token = data.read().strip()

        
        bot = LichessBot(engine, token)
        if args.stats:
            bot.stats()
        else:
            bot.run()

    elif args.command == "game":
        from game import Game
        Game().run()
        
    elif args.command == "eval":
        Evaluator().evaluate(Model.load(args.model))
