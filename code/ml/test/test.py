from itertools import chain
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

ALL_FEATURE_GROUPS = ["mfcc", "chroma", "mel", "contrast", "tonnetz",
                      "tempogram", "rms", "spectral_flux", "onset", "tempo"]
RESULTS_CSV = "feature_combination_results.csv"

def normal_model():
    from training.model import train
    from training.model_evaluator import DanceModelEvaluator
    from config.paths import MODEL_PATH, SCALER_PATH, LABELS_PATH, FEATURES_CSV

    #main()
    #analyze_results()

    result = train(disabled_labels= ["foxtrott", "tango"],
          selected_features=all_groups,
          test_size=0.15
    )

    # results = []
    #
    # for i in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45]:
    #     print(f"Training with test size: {i}")
    #     result = train(
    #         disabled_labels=["foxtrott"],
    #         selected_features=all_groups,
    #         test_size=i
    #     )
    #
    #     results.append({
    #         "test_size": i,
    #         "loss": result["loss"],
    #         "accuracy": result["accuracy"]
    #     })
    #
    # df_results = pd.DataFrame(results)
    # print(df_results.to_string(index=False))


    evaluator = DanceModelEvaluator(
        model_path=MODEL_PATH,
        scaler_path=SCALER_PATH,
        labels_path=LABELS_PATH,
        features_csv=FEATURES_CSV
    )

    evaluator.load_resources()
    evaluator.evaluate_from_arrays(result["X_test"], result["y_test"], set_name="test")

    evaluator.evaluate_from_arrays(result["X_train"], result["y_train"], set_name="train")

    evaluator.evaluate_from_arrays(result["X_val"], result["y_val"], set_name="val")

def cnn_model():
    from training.model_cnn import train_model as train
    from training.model_evaluator import DanceModelEvaluator
    from config.paths import MODEL_PATH, SCALER_PATH, LABELS_PATH, FEATURES_CSV

    result = train(
        disabled_labels=["foxtrott", "tango"],
        test_size=0.15
    )

    # results = []
    # for i in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45]:
    #     print(f"Training with test size: {i}")
    #     r = train(
    #         disabled_labels=["foxtrott"],
    #         selected_features=all_groups,
    #         test_size=i,
    #         input_shape=None,
    #         num_classes=None
    #     )
    #     results.append({
    #         "test_size": i,
    #         "loss": r["loss"],
    #         "accuracy": r["accuracy"]
    #     })
    # df_results = pd.DataFrame(results)
    # print(df_results.to_string(index=False))


    evaluator = DanceModelEvaluator(
        model_path=MODEL_PATH,
        scaler_path=SCALER_PATH,
        labels_path=LABELS_PATH,
        features_csv=FEATURES_CSV
    )

    evaluator.load_resources()

    evaluator.evaluate_from_arrays_cnn(result["X_test"], result["y_test"], set_name="test_cnn")
    evaluator.evaluate_from_arrays_cnn(result["X_val"], result["y_val"], set_name="val_cnn")
    evaluator.evaluate_from_arrays_cnn(result["X_train"], result["y_train"], set_name="train_cnn")


if __name__ == "__main__":
    #normal_model()
    cnn_model()