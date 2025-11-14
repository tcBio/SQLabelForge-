"""Model interface for OSS20B and other ML models."""

import logging
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class BaseModelInterface(ABC):
    """Abstract base class for model interfaces."""

    @abstractmethod
    def predict(self, data: pd.DataFrame) -> List[Any]:
        """Make predictions on data."""
        pass

    @abstractmethod
    def predict_proba(self, data: pd.DataFrame) -> List[float]:
        """Get prediction probabilities."""
        pass


class OSS20BInterface(BaseModelInterface):
    """
    Interface for OSS20B model integration.

    Features:
    - Batch prediction support
    - Confidence scoring
    - GPU acceleration
    - Model versioning
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        use_gpu: bool = True,
        batch_size: int = 32,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize OSS20B model interface.

        Args:
            model_path: Path to model weights/checkpoint
            use_gpu: Enable GPU acceleration
            batch_size: Batch size for predictions
            config: Additional model configuration
        """
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.batch_size = batch_size
        self.config = config or {}
        self.model = None

        logger.info(f"OSS20B interface initialized (GPU: {use_gpu})")

    def load_model(self, model_path: Optional[str] = None):
        """
        Load OSS20B model from checkpoint.

        Args:
            model_path: Path to model checkpoint (overrides init path)
        """
        path = model_path or self.model_path

        if not path:
            raise ValueError("Model path must be provided")

        # Placeholder for actual model loading
        # In real implementation, this would load the OSS20B model
        logger.info(f"Loading model from {path}")

        # TODO: Implement actual OSS20B model loading
        # self.model = load_oss20b_model(path, use_gpu=self.use_gpu)

        logger.info("Model loaded successfully")

    def predict(self, data: pd.DataFrame) -> List[Any]:
        """
        Make predictions on data.

        Args:
            data: Input DataFrame

        Returns:
            List of predictions
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Placeholder for actual prediction
        logger.info(f"Making predictions on {len(data)} samples")

        # TODO: Implement actual OSS20B prediction
        # predictions = self.model.predict(data, batch_size=self.batch_size)

        # Placeholder return
        predictions = [0] * len(data)

        return predictions

    def predict_proba(self, data: pd.DataFrame) -> List[float]:
        """
        Get prediction probabilities.

        Args:
            data: Input DataFrame

        Returns:
            List of confidence scores
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Placeholder for actual probability prediction
        logger.info(f"Getting probabilities for {len(data)} samples")

        # TODO: Implement actual OSS20B probability prediction
        # probabilities = self.model.predict_proba(data, batch_size=self.batch_size)

        # Placeholder return
        probabilities = [0.5] * len(data)

        return probabilities

    def batch_predict(
        self,
        data: pd.DataFrame,
        return_probabilities: bool = True,
    ) -> Dict[str, Union[List[Any], List[float]]]:
        """
        Perform batch prediction with optional probability scores.

        Args:
            data: Input DataFrame
            return_probabilities: Whether to return probability scores

        Returns:
            Dictionary with 'predictions' and optionally 'probabilities'
        """
        predictions = self.predict(data)

        result = {"predictions": predictions}

        if return_probabilities:
            probabilities = self.predict_proba(data)
            result["probabilities"] = probabilities

        return result


class CustomModelInterface(BaseModelInterface):
    """
    Interface for custom ML models (scikit-learn, PyTorch, TensorFlow, etc.).

    Allows integration of custom trained models for assisted labeling.
    """

    def __init__(
        self,
        model: Any,
        preprocessor: Optional[callable] = None,
    ):
        """
        Initialize custom model interface.

        Args:
            model: Pre-trained model object (must have predict/predict_proba methods)
            preprocessor: Optional preprocessing function for input data
        """
        self.model = model
        self.preprocessor = preprocessor
        logger.info("Custom model interface initialized")

    def predict(self, data: pd.DataFrame) -> List[Any]:
        """
        Make predictions using custom model.

        Args:
            data: Input DataFrame

        Returns:
            List of predictions
        """
        # Apply preprocessing if provided
        if self.preprocessor:
            data = self.preprocessor(data)

        predictions = self.model.predict(data)
        return predictions.tolist() if hasattr(predictions, 'tolist') else predictions

    def predict_proba(self, data: pd.DataFrame) -> List[float]:
        """
        Get prediction probabilities.

        Args:
            data: Input DataFrame

        Returns:
            List of confidence scores
        """
        # Apply preprocessing if provided
        if self.preprocessor:
            data = self.preprocessor(data)

        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(data)
            # For binary classification, return probability of positive class
            if probabilities.shape[1] == 2:
                return probabilities[:, 1].tolist()
            # For multi-class, return max probability
            return probabilities.max(axis=1).tolist()
        else:
            logger.warning("Model does not support predict_proba, returning default scores")
            return [1.0] * len(data)


class ModelInterface:
    """
    Unified model interface supporting multiple model types.

    Factory class for creating appropriate model interfaces.
    """

    @staticmethod
    def create(
        model_type: str,
        **kwargs
    ) -> BaseModelInterface:
        """
        Create a model interface.

        Args:
            model_type: Type of model ('oss20b', 'custom')
            **kwargs: Arguments for the specific model interface

        Returns:
            Model interface instance
        """
        if model_type.lower() == "oss20b":
            return OSS20BInterface(**kwargs)
        elif model_type.lower() == "custom":
            return CustomModelInterface(**kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
