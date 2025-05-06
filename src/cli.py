import argparse
from model import Model
from engine import Engine
from infinite_dataset import InfiniteDataset
from lichess_bot import LichessBot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train or manage the model.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train the model")
    train_parser.add_argument(
        "--name", type=str, default="null", help="Optional name for the training run",
    )
    
    train_parser.add_argument(
        "--generate_data", type=bool, default=False, help="Generate new training data while training"
    )

    generate_parser = subparsers.add_parser("generate", help="Generate datasets")
    generate_parser.add_argument(
        "--batch_size", type=int, default=500, help="Number of samples per batch"
    )
    generate_parser.add_argument(
        "--num_files", type=int, default=10, help="Number of dataset files to generate"
    )
    
    lichess_parser = subparsers.add_parser("lichess", help="Host Lichess Bot")
    lichess_parser.add_argument(
        "--model", type=str, default="blundernet", help="Model to run in the engine"
    )
    lichess_parser.add_argument(
        "--challenge", action="store_true", help="Start a game by challenging a random bot"
    )


    args = parser.parse_args()

    if args.command == "train":
        dataset = InfiniteDataset(use_saved=not args.generate_data)
        
        if args.name == "null":
            Model.train(dataset)
        else:
            Model.train(dataset, args.name)

    elif args.command == "generate":
        InfiniteDataset.generate(batch_size=args.batch_size, num_batches=args.num_files)
        
    elif args.command == "lichess":
        model = args.model
        
        engine = Engine("blundernet6.keras")
        token = None
        
        with open(".lichess_token", "r") as data:
            token = data.read().strip()
            
        bot = LichessBot(engine, token)
        if args.challenge:
            bot.start_game_against_random_bot(["sargon-1ply", "Humaia", "LouisChess48-6K"])
        else:
            bot.run()
