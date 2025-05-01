import tensorflow as tf
from tensorflow.keras import layers, models
import json
import os
import utils
from chess import pgn
from datetime import datetime
from live_plot import LivePlot

tf.config.set_visible_devices([], 'GPU')


class Model:
    def __init__(self, move_dict, model):
        self.move_dict = move_dict
        self.model = model

    @staticmethod
    def _build_model(output_size):
        inputs = layers.Input(shape=(8, 8, 12))
        
        x = layers.Conv2D(64, (3, 3), strides=1, padding='same', activation='relu')(inputs)
        x = layers.BatchNormalization()(x)

        for _ in range(3):
            shortcut = x
            x = layers.Conv2D(64, (3, 3), padding='same', activation='relu')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Conv2D(64, (3, 3), padding='same')(x)
            x = layers.Add()([x, shortcut])
            x = layers.ReLU()(x)

        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(128, activation='relu')(x)
        outputs = layers.Dense(output_size)(x)

        model = models.Model(inputs=inputs, outputs=outputs)

        model.compile(
            optimizer='adam',
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy']
        )
        return model

    @staticmethod
    def train(model_name=None):
        move_dict = utils.generate_full_uci_move_dict()
        
        if model_name and os.path.exists(f"models/{model_name}.keras"):
            model = models.load_model(f"models/{model_name}.keras")
        elif not model_name:
            model_name = datetime.now().strftime("model_%Y%m%d_%H%M%S")
            print(f"No model name given, creating new model with name {model_name}")
            model = Model._build_model(len(move_dict))
        else:
            print(f"No model found named {model_name}, creating a new model...")
            model = Model._build_model(len(move_dict))
        
        instance = Model(move_dict, model)
        positions_processed = 0
        game_chunk = 1
        live_plot = LivePlot()
        
        try:
            for games in _get_training_data(500):
                board_positions, gold_standard, _ = utils.preprocess(games)

                if len(board_positions) == len(gold_standard):
                    history = model.fit(board_positions, gold_standard, epochs=1, batch_size=64)
                    if "accuracy" in history.history and "loss" in history.history:
                        acc = history.history["accuracy"][-1]
                        loss = history.history["loss"][-1]
                        live_plot.update(acc, loss)

                    positions_processed += len(board_positions)
                    instance.save(f"__engine__/models/{model_name}.keras")
                    
                    print(f"\033[92m\nGame chunk {game_chunk} completed! Total position processed is {positions_processed}\033[0m")
                    print("\033[33mPress CTRL+C to stop the training process, the model will be saved\n\033[0m")
                    game_chunk += 1
                    
            return instance
        except KeyboardInterrupt:
            print("\033[92mModel saved!\033[0m")

    @staticmethod
    def load(path):
        model = models.load_model(path)
        move_dict = utils.generate_full_uci_move_dict()
        return Model(move_dict, model)

    def fit(self, data, targets, epochs=10, batch_size=64):
        self.model.fit(data, targets, epochs=epochs, batch_size=batch_size)

    def save(self, path):
        self.model.save(path)
            


def _get_training_data(batch_size):
        games = []

        for filename in os.listdir("training_data"):
            path = os.path.join("training_data", filename)
            with open(path, "r") as game_data:
                while True:
                    game = pgn.read_game(game_data)
                    if game is None:
                        break
                    
                    if int(game.headers["BlackElo"]) > 1200:
                        games.append(game)
                    
                    if len(games) > batch_size:
                        yield games
                        games = []                       
                        
                

        return games
