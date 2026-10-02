import argparse
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier

from src.preprocessing import load_train_data, run_preproc


def main():
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-data', type=Path, default=directory.parent / 'data/train.csv')
    parser.add_argument('--sample-size', type=int, default=30000)
    parser.add_argument('--output', type=Path, default=directory / 'models/trained_catboost.cbm')
    args = parser.parse_args()

    data = pd.read_csv(args.train_data).sample(n=args.sample_size, random_state=42)
    data = data.reset_index(drop=True)
    target = data['target']

    statistics = load_train_data(args.train_data)
    features = run_preproc(statistics, data.drop(columns='target'))

    time_columns = ['hour', 'year', 'month', 'day_of_month', 'day_of_week']
    categorical_columns = [
        column for column in features.columns
        if column.endswith('_cat') or column in time_columns
    ]
    features[categorical_columns] = features[categorical_columns].astype(str)

    model = CatBoostClassifier(
        iterations=100,
        depth=5,
        learning_rate=0.1,
        random_seed=42,
        task_type='CPU',
        thread_count=4,
        allow_writing_files=False,
        verbose=25,
    )
    model.fit(features, target, cat_features=categorical_columns)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(args.output))
    print(f'Model saved to {args.output}')


if __name__ == '__main__':
    main()
