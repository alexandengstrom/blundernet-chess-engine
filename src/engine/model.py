import os
from datetime import datetime
import numpy as np
import chess

import tensorflow as tf
from tensorflow.keras import layers, models, regularizers

from utils import UCI_DICT, Logger
from engine.live_plot import LivePlot


class Model:
    def __init__(self, model, name):
        self.model = model
        self.name = name

    @staticmethod
    def _build_model(output_size):
        inputs = layers.Input(shape=(8, 8, 18))

        x = layers.Conv2D(128, kernel_size=3, padding="same", activation="relu")(inputs)
        x = layers.BatchNormalization()(x)

        for _ in range(10):
            shortcut = x
            x = layers.Conv2D(128, kernel_size=3, padding="same", activation="relu")(x)
            x = layers.BatchNormalization()(x)
            x = layers.Conv2D(128, kernel_size=3, padding="same")(x)
            x = layers.BatchNormalization()(x)
            x = layers.Add()([x, shortcut])
            x = layers.ReLU()(x)

        se = layers.GlobalAveragePooling2D()(x)
        se = layers.Dense(8, activation="relu")(se)
        se = layers.Dense(128, activation="sigmoid")(se)
        se = layers.Reshape((1, 1, 128))(se)
        x = layers.Multiply()([x, se])

        p = layers.Conv2D(2, kernel_size=1, activation="relu")(x)
        p = layers.BatchNormalization()(p)
        p = layers.Flatten()(p)
        p = layers.Dense(1024, activation="gelu")(p)
        p = layers.Dense(output_size)(p)

        model = models.Model(inputs=inputs, outputs=p)

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0003),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=["accuracy"],
        )

        return model


    def evaluate(self, data, labels, batch_size=64):
        results = self.model.evaluate(data, labels, batch_size=batch_size, verbose=1)
        loss, accuracy = results[0], results[1]
        Logger.info(f"Evaluation - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
        return loss, accuracy
    
    def predict(self, board: chess.Board):
        board_matrix = self.board_to_matrix(board)
        board_matrix = np.expand_dims(board_matrix, axis=0)
        prediction = self.model.predict(board_matrix, verbose=0)
        return prediction

    def train(self, dataset, batch_size: int):
        positions_processed = 0
        game_chunk = 1
        live_plot = LivePlot()
        model_path = os.path.join("models", f"{self.model.name}.keras")

        try:
            for board_positions, gold_standard in dataset:

                if len(board_positions) == len(gold_standard):
                    history = self.model.fit(
                        board_positions, gold_standard, epochs=1, batch_size=batch_size
                    )
                    if "accuracy" in history.history and "loss" in history.history:
                        acc = history.history["accuracy"][-1]
                        loss = history.history["loss"][-1]
                        live_plot.update(acc, loss)

                    positions_processed += len(board_positions)
                    self.model.save(model_path)

                    Logger.info(
                        f"\033[92m\nGame chunk {game_chunk} completed! Total position processed is {positions_processed}\033[0m"
                    )
                    Logger.info(
                        "\033[33mPress CTRL+C to stop the training process, the model will be saved\n\033[0m"
                    )
                    game_chunk += 1

        except KeyboardInterrupt:
            Logger.info("\033[92mModel saved!\033[0m")
            
    @staticmethod
    def board_to_matrix(board: chess.Board):
        matrix = np.zeros((8, 8, 18), dtype=np.float32)

        piece_map = board.piece_map()
        for square, piece in piece_map.items():
            row = square // 8
            col = square % 8
            piece_type = piece.piece_type - 1
            color_offset = 0 if piece.color == chess.WHITE else 6
            matrix[row, col, piece_type + color_offset] = 1

        if board.turn == chess.WHITE:
            matrix[:, :, 12] = 1

        if board.has_kingside_castling_rights(chess.WHITE):
            matrix[:, :, 13] = 1
        if board.has_queenside_castling_rights(chess.WHITE):
            matrix[:, :, 14] = 1
        if board.has_kingside_castling_rights(chess.BLACK):
            matrix[:, :, 15] = 1
        if board.has_queenside_castling_rights(chess.BLACK):
            matrix[:, :, 16] = 1
            
        move_count = board.fullmove_number / 200
        matrix[:, :, 17] = move_count

        return matrix

    @staticmethod
    def load(model_name):
        model = None
        model_path = os.path.join("models", f"{model_name}.keras") if model_name else None
        
        if model_name and os.path.exists(model_path):
            model = models.load_model(model_path)
        elif not model_name:
            model_name = datetime.now().strftime("model_%Y%m%d_%H%M%S")
            Logger.warning(f"No model name given, creating new model with name {model_name}")
            model = Model._build_model(len(UCI_DICT))
        else:
            Logger.warning(f"No model found named {model_name}, creating a new model...")
            model = Model._build_model(len(UCI_DICT))
        
        return Model(model, model_name)

    def fit(self, data, targets, epochs=10, batch_size=64):
        self.model.fit(data, targets, epochs=epochs, batch_size=batch_size)

    def save(self, path):
        self.model.save(path)
