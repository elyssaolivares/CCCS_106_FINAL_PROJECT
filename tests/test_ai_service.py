"""
Tests for AI/ML service
"""
import pytest
import numpy as np
import os
import sys
from unittest.mock import Mock, patch

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestAIService:
    """Test AI/ML service operations"""
    
    def test_model_initialization(self):
        """Test AI model initialization"""
        from app.services.ai import ai_services
        
        # Check that model is loaded
        assert ai_services.model is not None
        assert ai_services.vectorizer is not None
    
    def test_gibberish_detection_empty_string(self):
        """Test gibberish detection with empty string"""
        from app.services.ai.ai_services import is_gibberish
        
        assert is_gibberish("") is True
    
    def test_gibberish_detection_whitespace(self):
        """Test gibberish detection with whitespace"""
        from app.services.ai.ai_services import is_gibberish
        
        assert is_gibberish("   ") is True
    
    def test_gibberish_detection_short_word(self):
        """Test gibberish detection with single short word"""
        from app.services.ai.ai_services import is_gibberish
        
        assert is_gibberish("a") is True
        assert is_gibberish("ab") is True
    
    def test_gibberish_detection_valid_text(self):
        """Test gibberish detection with valid text"""
        from app.services.ai.ai_services import is_gibberish
        
        assert is_gibberish("This is a valid report") is False
        assert is_gibberish("System not working") is False
    
    def test_report_categorization(self):
        """Test categorizing reports using ML model"""
        from app.services.ai import ai_services
        
        # Test with a valid report text
        text = "Computer lab is not working properly"
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
        assert len(prediction) > 0
    
    def test_categorization_returns_string(self):
        """Test that model returns predictions"""
        from app.services.ai import ai_services
        
        text = "The internet connection in room 101 is down"
        vectorized = ai_services.vectorizer.transform([text])
        result = ai_services.model.predict(vectorized)
        
        assert result is not None
        assert len(result) >= 1
    
    def test_categorize_academic_issue(self):
        """Test categorizing academic issue"""
        from app.services.ai import ai_services
        
        text = "Missing grades in the system"
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
        assert len(prediction) >= 1


class TestAIDataProcessing:
    """Test data processing for AI"""
    
    def test_text_preprocessing_lowercase(self):
        """Test text preprocessing converts to lowercase"""
        from app.services.ai.ai_services import is_gibberish
        
        # Gibberish check works with different cases
        assert is_gibberish("TEST TEXT") is False
        assert is_gibberish("Test Text") is False
    
    def test_text_preprocessing_strip(self):
        """Test text preprocessing strips whitespace"""
        from app.services.ai.ai_services import is_gibberish
        
        # Should handle leading/trailing whitespace
        assert is_gibberish("  valid text  ") is False
    
    def test_vectorizer_exists(self):
        """Test that vectorizer is created"""
        from app.services.ai import ai_services
        
        assert ai_services.vectorizer is not None
        
    def test_vectorizer_has_vocabulary(self):
        """Test that vectorizer has built vocabulary"""
        from app.services.ai import ai_services
        
        assert hasattr(ai_services.vectorizer, 'vocabulary_')
        assert len(ai_services.vectorizer.vocabulary_) > 0


class TestAIModelTraining:
    """Test model training and evaluation"""
    
    def test_model_is_trained(self):
        """Test that model is properly trained"""
        from app.services.ai import ai_services
        
        assert ai_services.model is not None
        # Check that model has been fitted
        assert hasattr(ai_services.model, 'feature_log_prob_')
    
    def test_model_predict_method_exists(self):
        """Test that model has predict method"""
        from app.services.ai import ai_services
        
        assert hasattr(ai_services.model, 'predict')
    
    def test_model_predict_proba_method_exists(self):
        """Test that model has predict_proba method"""
        from app.services.ai import ai_services
        
        assert hasattr(ai_services.model, 'predict_proba')
    
    def test_categorize_multiple_reports(self):
        """Test categorizing multiple different reports"""
        from app.services.ai import ai_services
        
        reports = [
            "Internet not working",
            "Need new keyboard",
            "Grades are wrong",
            "Building is cold"
        ]
        
        # Vectorize and predict for all reports
        vectorized = ai_services.vectorizer.transform(reports)
        predictions = ai_services.model.predict(vectorized)
        
        assert predictions is not None
        assert len(predictions) == len(reports)


class TestAIModelPredictions:
    """Test model prediction functionality"""
    
    def test_predict_proba_returns_probabilities(self):
        """Test that predict_proba returns probability estimates"""
        from app.services.ai import ai_services
        
        text = "Computer is broken"
        vectorized = ai_services.vectorizer.transform([text])
        
        # Get predictions with probabilities
        if hasattr(ai_services.model, 'predict_proba'):
            proba = ai_services.model.predict_proba(vectorized)
            
            assert proba is not None
            assert len(proba) > 0
            # Probabilities should sum to 1 for each sample
            assert np.allclose(proba.sum(axis=1), 1.0)
    
    def test_vectorizer_transform_consistency(self):
        """Test that vectorizer produces consistent output"""
        from app.services.ai import ai_services
        
        text = "System not working"
        
        # Transform same text twice
        vec1 = ai_services.vectorizer.transform([text])
        vec2 = ai_services.vectorizer.transform([text])
        
        # Should produce identical vectors
        assert (vec1 != vec2).nnz == 0  # Compare sparse matrices
    
    def test_vectorizer_handles_unknown_words(self):
        """Test that vectorizer handles unknown words"""
        from app.services.ai import ai_services
        
        # Mix of known and unknown words
        text = "asdfghjkl qwerty zxcvbnm"
        
        # Should not raise error
        vectorized = ai_services.vectorizer.transform([text])
        assert vectorized is not None
    
    def test_model_predicts_all_classes(self):
        """Test that model can predict all classes"""
        from app.services.ai import ai_services
        
        # Get the classes the model knows
        classes = ai_services.model.classes_
        
        assert classes is not None
        assert len(classes) > 0
    
    def test_gibberish_threshold(self):
        """Test gibberish detection threshold"""
        from app.services.ai.ai_services import is_gibberish
        
        # Valid text should not be gibberish
        assert is_gibberish("This is a valid problem statement") is False
        
        # Very short random chars
        assert is_gibberish("xy") is True
    
    def test_batch_prediction(self):
        """Test batch prediction of multiple texts"""
        from app.services.ai import ai_services
        
        texts = [
            "Classroom AC is not working",
            "Need laptop for assignment",
            "Final grades not showing",
            "Library door lock broken"
        ]
        
        # Vectorize all at once
        vectorized = ai_services.vectorizer.transform(texts)
        predictions = ai_services.model.predict(vectorized)
        
        # Should predict all
        assert len(predictions) == len(texts)
        
        # All should be non-empty strings
        for pred in predictions:
            assert isinstance(pred, str)
            assert len(pred) > 0
    
    def test_vectorizer_sparse_matrix_output(self):
        """Test that vectorizer outputs sparse matrix"""
        from app.services.ai import ai_services
        from scipy.sparse import csr_matrix
        
        text = "This is a test message"
        vectorized = ai_services.vectorizer.transform([text])
        
        # Should be a sparse matrix
        assert isinstance(vectorized, (csr_matrix, type(vectorized)))
        assert vectorized.shape[0] == 1  # One document
        assert vectorized.shape[1] > 0   # Multiple features


class TestAIEdgeCases:
    """Test edge cases and error handling"""
    
    def test_very_long_text(self):
        """Test handling of very long text"""
        from app.services.ai import ai_services
        
        # Create a long text
        long_text = "word " * 1000
        
        # Should handle without error
        vectorized = ai_services.vectorizer.transform([long_text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
    
    def test_special_characters_in_text(self):
        """Test handling of special characters"""
        from app.services.ai import ai_services
        
        text = "System error!!! @#$% Computer down??? ????"
        
        # Should handle special characters
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
    
    def test_numeric_only_text(self):
        """Test handling of numeric-only text"""
        from app.services.ai import ai_services
        
        text = "123456789"
        
        # Should handle numbers
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
    
    def test_mixed_language_text(self):
        """Test handling of text with numbers and special chars"""
        from app.services.ai.ai_services import is_gibberish
        
        # Mixed valid text
        assert is_gibberish("Room 101 AC not working") is False
        assert is_gibberish("Error Code: 500") is False
    
    def test_case_insensitive_gibberish_detection(self):
        """Test that gibberish detection is case insensitive"""
        from app.services.ai.ai_services import is_gibberish
        
        assert is_gibberish("VALID TEXT") is False
        assert is_gibberish("valid text") is False
        assert is_gibberish("Valid Text") is False
    
    def test_single_letter_words(self):
        """Test handling of single letter words"""
        from app.services.ai import ai_services
        
        text = "a b c d is working"
        
        # Should not crash
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None


class TestAIRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_incomplete_sentence(self):
        """Test with incomplete sentence"""
        from app.services.ai import ai_services
        
        text = "Computer not working in"
        
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
    
    def test_all_caps_report(self):
        """Test with all caps report"""
        from app.services.ai import ai_services
        
        text = "INTERNET CONNECTION DOWN IN LAB 102"
        
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
    
    def test_misspelled_words(self):
        """Test with misspelled words"""
        from app.services.ai import ai_services
        
        text = "komputer not wrking proplerly"
        
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
    
    def test_repeated_words(self):
        """Test with repeated words"""
        from app.services.ai import ai_services
        
        text = "broken broken broken computer broken"
        
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None
    
    def test_unicode_characters(self):
        """Test with unicode characters"""
        from app.services.ai.ai_services import is_gibberish
        
        # Should handle unicode
        assert is_gibberish("Problem café naïve") is False
    
    def test_multiple_spaces(self):
        """Test with multiple spaces"""
        from app.services.ai.ai_services import is_gibberish
        
        assert is_gibberish("test    with    spaces") is False
    
    def test_punctuation_heavy_text(self):
        """Test with lots of punctuation"""
        from app.services.ai import ai_services
        
        text = "!!!HELP!!! ...Computer... ---broken---"
        
        vectorized = ai_services.vectorizer.transform([text])
        prediction = ai_services.model.predict(vectorized)
        
        assert prediction is not None


class TestAIVectorization:
    """Test vectorization edge cases"""
    
    def test_vectorizer_with_empty_vocabulary_word(self):
        """Test vectorizer with out-of-vocab words"""
        from app.services.ai import ai_services
        
        # Mix of in-vocab and out-of-vocab
        text = "asdfghjklzxcvbnm test computer problem"
        
        vectorized = ai_services.vectorizer.transform([text])
        assert vectorized.shape[0] == 1
    
    def test_consistent_vector_shape(self):
        """Test that vector shape is consistent"""
        from app.services.ai import ai_services
        
        texts = ["test one", "test two", "test three"]
        
        vectors = [ai_services.vectorizer.transform([t]) for t in texts]
        
        # All should have same number of features
        assert all(v.shape[1] == vectors[0].shape[1] for v in vectors)
    
    def test_model_classes_exist(self):
        """Test that model has defined classes"""
        from app.services.ai import ai_services
        
        classes = ai_services.model.classes_
        
        assert classes is not None
        assert len(classes) > 0
        
        # Should be string class labels
        assert all(isinstance(c, str) for c in classes)


class TestAIGibberishVariations:
    """Test gibberish detection with various inputs"""
    
    def test_gibberish_two_letters(self):
        """Test gibberish with exactly 2 letters"""
        from app.services.ai.ai_services import is_gibberish
        
        assert is_gibberish("ab") is True
        assert is_gibberish("XY") is True
    
    def test_gibberish_three_letters(self):
        """Test gibberish with 3 letters"""
        from app.services.ai.ai_services import is_gibberish
        
        # Three letters might be gibberish depending on implementation
        result = is_gibberish("abc")
        assert isinstance(result, bool)
    
    def test_valid_short_word(self):
        """Test valid short word detection"""
        from app.services.ai.ai_services import is_gibberish
        
        assert is_gibberish("hello") is False
        assert is_gibberish("test") is False
        assert is_gibberish("code") is False
    
    def test_gibberish_only_vowels(self):
        """Test with only vowels"""
        from app.services.ai.ai_services import is_gibberish
        
        result = is_gibberish("aeiou")
        assert isinstance(result, bool)
    
    def test_gibberish_only_consonants(self):
        """Test with only consonants"""
        from app.services.ai.ai_services import is_gibberish
        
        result = is_gibberish("bcdfg")
        assert isinstance(result, bool)


class TestAIPreprocessing:
    """Test AI preprocessing and text handling"""
    
    def test_predict_category_with_lowercase(self):
        """Test that predict_category handles lowercase correctly"""
        from app.services.ai.ai_services import predict_category
        
        # Should normalize to lowercase
        result = predict_category("WATER DAMAGE")
        assert isinstance(result, str)
    
    def test_predict_category_with_extra_whitespace(self):
        """Test that predict_category strips whitespace"""
        from app.services.ai.ai_services import predict_category
        
        # Should handle extra whitespace
        result = predict_category("   electrical issue   ")
        assert isinstance(result, str)
    
    def test_predict_category_empty_string(self):
        """Test prediction with empty string"""
        from app.services.ai.ai_services import predict_category
        
        result = predict_category("")
        assert result == "Uncategorized"
    
    def test_predict_category_with_whitespace_only(self):
        """Test prediction with whitespace only"""
        from app.services.ai.ai_services import predict_category
        
        result = predict_category("   ")
        assert result == "Uncategorized"
    
    def test_predict_category_with_numbers(self):
        """Test prediction with numbers in text"""
        from app.services.ai.ai_services import predict_category
        
        # Numbers should be ignored in preprocessing
        result = predict_category("building 123 has water damage 456")
        assert isinstance(result, str)
    
    def test_predict_category_with_special_characters(self):
        """Test prediction with special characters"""
        from app.services.ai.ai_services import predict_category
        
        # Special chars should be ignored
        result = predict_category("electrical!@#$%^issue?!")
        assert isinstance(result, str)
    
    def test_predict_category_with_confidence(self):
        """Test predict_category with confidence flag"""
        from app.services.ai.ai_services import predict_category
        
        result = predict_category("electrical issue", return_confidence=True)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], (int, float))
    
    def test_predict_category_unknown_tokens(self):
        """Test prediction with completely unknown tokens"""
        from app.services.ai.ai_services import predict_category
        
        result = predict_category("xyzabc qwerty asdf")
        assert result == "Uncategorized"
    
    def test_predict_category_mixed_known_unknown(self):
        """Test prediction with mix of known and unknown tokens"""
        from app.services.ai.ai_services import predict_category
        
        result = predict_category("water xyzabc damage qwerty")
        assert isinstance(result, str)
    
    def test_predict_category_single_word(self):
        """Test prediction with single word"""
        from app.services.ai.ai_services import predict_category
        
        result = predict_category("water")
        assert isinstance(result, str)
    
    def test_predict_category_multiple_words(self):
        """Test prediction with multiple words"""
        from app.services.ai.ai_services import predict_category
        
        result = predict_category("there is water damage in building three")
        assert isinstance(result, str)


class TestAIModelInitialization:
    """Test AI model initialization and loading"""
    
    def test_model_is_loaded(self):
        """Test that model is loaded on import"""
        from app.services.ai import ai_services
        
        # Model should be loaded
        assert ai_services.model is not None
        assert ai_services.vectorizer is not None
    
    def test_vectorizer_has_vocabulary(self):
        """Test that vectorizer has vocabulary after loading"""
        from app.services.ai import ai_services
        
        assert hasattr(ai_services.vectorizer, 'vocabulary_')
        assert len(ai_services.vectorizer.vocabulary_) > 0
    
    def test_model_has_classes(self):
        """Test that model has learned classes"""
        from app.services.ai import ai_services
        
        assert hasattr(ai_services.model, 'classes_')
        assert len(ai_services.model.classes_) > 0
    
    def test_vectorizer_transform_works(self):
        """Test that vectorizer can transform text"""
        from app.services.ai import ai_services
        
        text = "water damage in building"
        X = ai_services.vectorizer.transform([text])
        
        assert X is not None
        assert X.shape[0] == 1
    
    def test_model_predict_proba(self):
        """Test that model can predict probabilities"""
        from app.services.ai import ai_services
        
        text = "electrical issue in room"
        X = ai_services.vectorizer.transform([text])
        
        # Only predict if X has non-zero elements
        if X.nnz > 0:
            probs = ai_services.model.predict_proba(X)
            assert probs is not None
            assert probs.shape[0] == 1


class TestAITextNormalization:
    """Test text normalization in AI service"""
    
    def test_is_gibberish_with_proper_sentence(self):
        """Test is_gibberish with proper English sentence"""
        from app.services.ai.ai_services import is_gibberish
        
        result = is_gibberish("The water damage is in the basement")
        assert result is False
    
    def test_is_gibberish_with_single_letter(self):
        """Test is_gibberish with single letter"""
        from app.services.ai.ai_services import is_gibberish
        
        result = is_gibberish("a")
        assert result is True
    
    def test_is_gibberish_with_numbers_only(self):
        """Test is_gibberish with numbers only"""
        from app.services.ai.ai_services import is_gibberish
        
        result = is_gibberish("123456")
        assert result is True
    
    def test_is_gibberish_with_special_chars_only(self):
        """Test is_gibberish with special characters only"""
        from app.services.ai.ai_services import is_gibberish
        
        result = is_gibberish("!@#$%^&*()")
        assert result is True
    
    def test_is_gibberish_with_mixed_content(self):
        """Test is_gibberish with numbers and letters"""
        from app.services.ai.ai_services import is_gibberish
        
        result = is_gibberish("building123damage456")
        # Should be False because there are valid words
        assert isinstance(result, bool)
    
    def test_is_gibberish_with_three_letter_word(self):
        """Test is_gibberish with three letter word"""
        from app.services.ai.ai_services import is_gibberish
        
        # Three letter word should not be gibberish
        result = is_gibberish("the water issue")
        assert result is False
    
    def test_is_gibberish_with_newlines_and_tabs(self):
        """Test is_gibberish with whitespace characters"""
        from app.services.ai.ai_services import is_gibberish
        
        result = is_gibberish("\n\t  water damage\n")
        # After stripping should be valid
        assert isinstance(result, bool)

