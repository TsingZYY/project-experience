"""Leakage-safe feature engineering, modeling, and validation for Titanic."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted


TARGET_COLUMN = "Survived"
RAW_INPUT_COLUMNS = (
    "PassengerId",
    "Pclass",
    "Name",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Ticket",
    "Fare",
    "Cabin",
    "Embarked",
)

NUMERIC_FEATURES = (
    "Age",
    "SibSp",
    "Parch",
    "FareLog",
    "FamilySize",
    "IsAlone",
)

TICKET_GROUP_FEATURE = "TicketGroupSize"
FARE_PER_PERSON_FEATURE = "FarePerPersonLog"
FAMILY_SIZE_CATEGORY_FEATURE = "FamilySizeCategory"

CATEGORICAL_FEATURES = (
    "Pclass",
    "Sex",
    "Embarked",
    "Title",
    "CabinDeck",
)


class TitanicFeatureEngineer(BaseEstimator, TransformerMixin):
    """Create row-level Titanic features inside a sklearn Pipeline.

    Common titles are learned only from the data passed to ``fit``. During
    cross-validation this means validation-fold title frequencies cannot leak
    into the training fold.
    """

    def __init__(
        self,
        min_title_frequency: int = 10,
        include_ticket_group_size: bool = False,
        include_fare_per_person: bool = False,
        include_family_size_category: bool = False,
    ):
        self.min_title_frequency = min_title_frequency
        self.include_ticket_group_size = include_ticket_group_size
        self.include_fare_per_person = include_fare_per_person
        self.include_family_size_category = include_family_size_category

    @staticmethod
    def _check_columns(frame: pd.DataFrame) -> None:
        missing = sorted(set(RAW_INPUT_COLUMNS) - set(frame.columns))
        if missing:
            raise ValueError(f"Missing required raw columns: {missing}")

    @staticmethod
    def _extract_titles(names: pd.Series) -> pd.Series:
        titles = (
            names.astype("string")
            .str.extract(r",\s*([^.]*)\.", expand=False)
            .str.strip()
            .fillna("Unknown")
        )
        return titles.replace(
            {
                "Mlle": "Miss",
                "Ms": "Miss",
                "Mme": "Mrs",
            }
        )

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None):
        frame = pd.DataFrame(X).copy()
        self._check_columns(frame)
        if self.min_title_frequency < 1:
            raise ValueError("min_title_frequency must be at least 1")

        title_counts = self._extract_titles(frame["Name"]).value_counts()
        self.common_titles_ = tuple(
            sorted(title_counts[title_counts >= self.min_title_frequency].index)
        )
        ticket_values = frame["Ticket"].astype("string").fillna("Unknown")
        self.ticket_counts_ = ticket_values.value_counts().to_dict()
        self.feature_names_in_ = np.asarray(frame.columns, dtype=object)
        self.n_features_in_ = frame.shape[1]
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        check_is_fitted(self, attributes=["common_titles_", "feature_names_in_"])
        frame = pd.DataFrame(X).copy()
        self._check_columns(frame)

        titles = self._extract_titles(frame["Name"])
        frame["Title"] = titles.where(titles.isin(self.common_titles_), "Rare")

        frame["FamilySize"] = frame["SibSp"] + frame["Parch"] + 1
        frame["IsAlone"] = (frame["FamilySize"] == 1).astype(int)

        if self.include_family_size_category:
            frame[FAMILY_SIZE_CATEGORY_FEATURE] = pd.cut(
                frame["FamilySize"],
                bins=[0, 1, 4, np.inf],
                labels=["Alone", "Small", "Large"],
            ).astype("string")

        cabins = frame["Cabin"].astype("string").str.strip()
        frame["CabinDeck"] = cabins.str[:1].fillna("Unknown").replace("", "Unknown")

        non_negative_fare = pd.to_numeric(frame["Fare"], errors="coerce").clip(lower=0)
        frame["FareLog"] = np.log1p(non_negative_fare)

        numeric_features = list(NUMERIC_FEATURES)
        if self.include_ticket_group_size:
            ticket_values = frame["Ticket"].astype("string").fillna("Unknown")
            # Counts are learned from the current training fold only.
            frame[TICKET_GROUP_FEATURE] = (
                ticket_values.map(self.ticket_counts_).fillna(1).astype(float)
            )
            numeric_features.append(TICKET_GROUP_FEATURE)

        if self.include_fare_per_person:
            ticket_values = frame["Ticket"].astype("string").fillna("Unknown")
            observed_group_size = ticket_values.map(self.ticket_counts_).fillna(1).clip(lower=1)
            fare_per_person = non_negative_fare / observed_group_size
            frame[FARE_PER_PERSON_FEATURE] = np.log1p(fare_per_person)
            numeric_features.append(FARE_PER_PERSON_FEATURE)

        categorical_features = list(CATEGORICAL_FEATURES)
        if self.include_family_size_category:
            categorical_features.append(FAMILY_SIZE_CATEGORY_FEATURE)

        selected = numeric_features + categorical_features
        return frame.loc[:, selected]

    def get_feature_names_out(self, input_features=None) -> np.ndarray:
        check_is_fitted(self, attributes=["common_titles_"])
        numeric_features = list(NUMERIC_FEATURES)
        if self.include_ticket_group_size:
            numeric_features.append(TICKET_GROUP_FEATURE)
        if self.include_fare_per_person:
            numeric_features.append(FARE_PER_PERSON_FEATURE)
        categorical_features = list(CATEGORICAL_FEATURES)
        if self.include_family_size_category:
            categorical_features.append(FAMILY_SIZE_CATEGORY_FEATURE)
        return np.asarray(numeric_features + categorical_features, dtype=object)


def make_preprocessor(
    *,
    include_ticket_group_size: bool = False,
    include_fare_per_person: bool = False,
    include_family_size_category: bool = False,
) -> ColumnTransformer:
    """Build preprocessing whose learned state is fit only on training data."""

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "one_hot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    numeric_features = list(NUMERIC_FEATURES)
    if include_ticket_group_size:
        numeric_features.append(TICKET_GROUP_FEATURE)
    if include_fare_per_person:
        numeric_features.append(FARE_PER_PERSON_FEATURE)
    categorical_features = list(CATEGORICAL_FEATURES)
    if include_family_size_category:
        categorical_features.append(FAMILY_SIZE_CATEGORY_FEATURE)

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


def make_model_candidates(random_state: int = 42) -> Mapping[str, BaseEstimator]:
    """Return the four deliberately bounded teaching candidates."""

    return {
        "Dummy": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(max_iter=2_000, random_state=random_state),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            random_state=random_state,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(random_state=random_state),
    }


def make_pipeline(
    model: BaseEstimator,
    *,
    include_ticket_group_size: bool = False,
    include_fare_per_person: bool = False,
    include_family_size_category: bool = False,
) -> Pipeline:
    """Combine feature creation, preprocessing, and a fresh model instance."""

    return Pipeline(
        steps=[
            (
                "features",
                TitanicFeatureEngineer(
                    include_ticket_group_size=include_ticket_group_size,
                    include_fare_per_person=include_fare_per_person,
                    include_family_size_category=include_family_size_category,
                ),
            ),
            (
                "preprocess",
                make_preprocessor(
                    include_ticket_group_size=include_ticket_group_size,
                    include_fare_per_person=include_fare_per_person,
                    include_family_size_category=include_family_size_category,
                ),
            ),
            ("model", clone(model)),
        ]
    )


def validate_raw_data(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    strict_competition_shape: bool = True,
) -> None:
    """Validate the official competition schema and key row-level invariants."""

    missing_train = sorted((set(RAW_INPUT_COLUMNS) | {TARGET_COLUMN}) - set(train.columns))
    missing_test = sorted(set(RAW_INPUT_COLUMNS) - set(test.columns))
    if missing_train:
        raise ValueError(f"Training data is missing columns: {missing_train}")
    if missing_test:
        raise ValueError(f"Test data is missing columns: {missing_test}")
    if TARGET_COLUMN in test.columns:
        raise ValueError("Test data must not contain the Survived target")

    if strict_competition_shape and (len(train) != 891 or len(test) != 418):
        raise ValueError(
            "Official Titanic data should contain 891 training rows and 418 test rows; "
            f"received {len(train)} and {len(test)}."
        )

    for label, frame in (("train", train), ("test", test)):
        if frame["PassengerId"].isna().any():
            raise ValueError(f"{label} contains missing PassengerId values")
        if not frame["PassengerId"].is_unique:
            raise ValueError(f"{label} contains duplicate PassengerId values")

    if train[TARGET_COLUMN].isna().any():
        raise ValueError("Training target contains missing values")
    target_values = set(train[TARGET_COLUMN].astype(int).unique())
    if not target_values.issubset({0, 1}) or len(target_values) != 2:
        raise ValueError(f"Training target must contain both binary classes; found {target_values}")


def validate_submission(submission: pd.DataFrame, test: pd.DataFrame) -> None:
    """Fail fast if a generated file would violate the Kaggle submission contract."""

    if list(submission.columns) != ["PassengerId", "Survived"]:
        raise ValueError("Submission columns must be exactly PassengerId, Survived")
    if len(submission) != len(test):
        raise ValueError("Submission row count must equal the test row count")
    if not submission["PassengerId"].is_unique:
        raise ValueError("Submission PassengerId values must be unique")
    expected_ids = test["PassengerId"].reset_index(drop=True)
    actual_ids = submission["PassengerId"].reset_index(drop=True)
    if not actual_ids.equals(expected_ids):
        raise ValueError("Submission PassengerId order must match test.csv")
    if not pd.api.types.is_integer_dtype(submission["Survived"]):
        raise ValueError("Submission predictions must use an integer dtype")
    prediction_values = set(submission["Survived"].unique())
    if not prediction_values.issubset({0, 1}):
        raise ValueError(f"Submission predictions must be 0 or 1; found {prediction_values}")
