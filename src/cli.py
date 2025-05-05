import argparse
from model import Model
from infinite_dataset import InfiniteDataset

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

    args = parser.parse_args()

    if args.command == "train":
        dataset = InfiniteDataset(use_saved=not args.generate_data)
        
        if args.name == "null":
            Model.train(dataset)
        else:
            Model.train(dataset, args.name)

    elif args.command == "generate":
        InfiniteDataset.generate(batch_size=args.batch_size, num_batches=args.num_files)
