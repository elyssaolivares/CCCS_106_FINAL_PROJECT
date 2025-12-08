

# Inline Docstrings for Core Services

Add these docstrings to the top of your specific Python files. They explain **what** the code does and **why**, which is critical for code review.

#### A. AI Service (`app/services/ai/ai_services.py`)

```python
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

class AICategorizer:
    """
    Service responsible for the automatic classification of maintenance reports.

    This class loads the training data from 'dataset.csv', trains a 
    Multinomial Naive Bayes model on startup, and provides a prediction 
    endpoint for new report descriptions.

    Attributes:
        vectorizer (CountVectorizer): Converts text to token counts.
        model (MultinomialNB): The trained classification model.
    """

    def __init__(self):
        """Initializes and trains the model immediately upon instantiation."""
        self._train_model()

    def predict_category(self, description: str) -> str:
        """
        Predicts the maintenance category for a given issue description.

        Args:
            description (str): The user-submitted text (e.g., "The lights are flickering").

        Returns:
            str: The predicted category (e.g., "Electrical").
        """
        # ... implementation code ...
```

#### B. Audit Logger (`app/services/audit/audit_logger.py`)

```python
import csv
import datetime
import os

class AuditLogger:
    """
    Handles the immutable logging of system events for security and accountability.
    
    This service writes events directly to a CSV file in the root directory.
    It is designed to be fail-safe; if writing fails, it should not crash the app.
    """

    LOG_FILE = f"audit_logs_{datetime.datetime.now().strftime('%Y%m%d')}.csv"

    @staticmethod
    def log_event(user_id: str, action_type: str, details: str):
        """
        Appends a new event to the daily audit log.

        Args:
            user_id (str): The Google Email or ID of the actor.
            action_type (str): Category of action (e.g., 'LOGIN_SUCCESS', 'REPORT_SUBMITTED').
            details (str): Contextual information (e.g., 'Report ID: 105').
        
        Raises:
            IOError: If the file system is read-only (handled internally).
        """
        # ... implementation code ...
```

#### C. Google Auth (`app/services/google/google_auth.py`)

```python
class GoogleAuthService:
    """
    Manages the OAuth 2.0 authentication flow with Google Identity Services.

    This service handles the generation of the authorization URL and 
    the exchange of the authorization code for an access token.
    It strictly validates that the user belongs to the institutional domain.
    """

    def get_login_url(self):
        """
        Generates the Google Sign-In URL for the Flet frontend.
        """
        # ...

    def validate_user(self, token):
        """
        Decodes the ID Token to verify user identity.

        Returns:
            dict: User profile (email, name, picture) if valid.
            None: If validation fails or domain is unauthorized.
        """
        # ...
```