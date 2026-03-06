"""
Multilingual Accessibility Service

This module provides multilingual distress keyword detection and emergency text
alert processing. It supports distress keywords in multiple Indian languages
and automatically triggers panic alerts when distress is detected.
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import re

from ..crud import crud_tourist
from ..services import alert_service, ledger_service
from ..db import models


# Multilingual distress keywords dictionary
# Each language includes common distress words and their variations
DISTRESS_KEYWORDS = {
    "english": [
        "help", "emergency", "urgent", "danger", "lost", "stuck", 
        "panic", "rescue", "save", "sos", "trouble", "assistance",
        "911", "police", "hospital", "ambulance", "fire"
    ],
    "hindi": [
        "मदद", "सहायता", "बचाओ", "आपातकाल", "खतरा", "गुम", 
        "फंसा", "पुलिस", "अस्पताल", "एम्बुलेंस", "आग", "समस्या"
    ],
    "bengali": [
        "সাহায্য", "সহায়তা", "বাঁচাও", "জরুরি", "বিপদ", "হারিয়ে", 
        "আটকে", "পুলিশ", "হাসপাতাল", "অ্যাম্বুলেন্স", "আগুন", "সমস্যা"
    ],
    "tamil": [
        "உதவி", "உதவுங்கள்", "காப்பாற்று", "அவசரம்", "ஆபத்து", "தொலைந்து", 
        "சிக்கி", "போலீஸ்", "மருத்துவமனை", "ஆம்புலன்ஸ்", "தீ", "பிரச்சனை"
    ],
    "telugu": [
        "సహాయం", "సహాయం చేయండి", "రక్షించు", "అత్యవసరం", "ప్రమాదం", "పోయింది",
        "చిక్కుకున్న", "పోలీసు", "ఆసుపత్రి", "అంబులెన్స్", "అగ్ని", "సమస్య"
    ],
    "marathi": [
        "मदत", "साहाय्य", "वाचवा", "तातडीची", "धोका", "हरवले",
        "अडकले", "पोलिस", "रुग्णालय", "रुग्णवाहिका", "आग", "समस्या"
    ],
    "gujarati": [
        "મદદ", "સહાય", "બચાવો", "તાત્કાલિક", "જોખમ", "ખોવાયેલ",
        "અટવાયેલ", "પોલીસ", "હોસ્પિટલ", "એમ્બ્યુલન્સ", "આગ", "સમસ્યા"
    ],
    "kannada": [
        "ಸಹಾಯ", "ಸಹಾಯ ಮಾಡಿ", "ಉಳಿಸು", "ತುರ್ತು", "ಅಪಾಯ", "ಕಳೆದುಹೋಗಿದೆ",
        "ಸಿಕ್ಕಿಕೊಂಡಿದೆ", "ಪೊಲೀಸ್", "ಆಸ್ಪತ್ರೆ", "ಆಂಬುಲೆನ್ಸ್", "ಬೆಂಕಿ", "ಸಮಸ್ಯೆ"
    ]
}

# Emotional distress patterns (for advanced detection)
DISTRESS_PATTERNS = [
    r'\b(scared|afraid|frightened|terrified)\b',
    r'\b(alone|isolated|stranded)\b',
    r'\b(hurt|injured|bleeding|pain)\b',
    r'\b(can\'t find|don\'t know where|location unknown)\b',
    r'\b(battery low|phone dying|no signal)\b'
]


async def process_text_alert(
    db: Session, 
    tourist_id: str, 
    text_message: str, 
    location_data: dict
) -> bool:
    """
    Process incoming text message for distress keywords and trigger alerts if needed
    
    This function analyzes text messages for distress keywords in multiple languages
    and automatically triggers the full panic alert workflow if distress is detected.
    It provides accessibility for tourists who may not be able to press panic buttons.
    
    Args:
        db: Database session for executing operations
        tourist_id: UUID string of the tourist sending the message
        text_message: The text message content to analyze
        location_data: Dictionary with latitude and longitude
        
    Returns:
        bool: True if distress detected and alert triggered, False otherwise
        
    Raises:
        Exception: If alert processing fails
        
    Example:
        >>> location = {"latitude": 40.7128, "longitude": -74.0060}
        >>> result = await process_text_alert(db, "123e4567", "मदद करो", location)
        >>> print(result)  # True - Hindi distress detected
        
        >>> result = await process_text_alert(db, "123e4567", "hello there", location)
        >>> print(result)  # False - No distress detected
    """
    try:
        # Step 1: Normalize the text message for analysis
        normalized_message = text_message.lower().strip()
        
        # Step 2: Check for distress keywords in all supported languages
        distress_detected = False
        detected_language = None
        detected_keyword = None
        
        # Check each language's keywords
        for language, keywords in DISTRESS_KEYWORDS.items():
            for keyword in keywords:
                # For non-English languages, do exact matching
                # For English, do word boundary matching to avoid false positives
                if language == "english":
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                    if re.search(pattern, normalized_message):
                        distress_detected = True
                        detected_language = language
                        detected_keyword = keyword
                        break
                else:
                    # Direct substring matching for non-English languages
                    if keyword in text_message:  # Use original case for Unicode matching
                        distress_detected = True
                        detected_language = language
                        detected_keyword = keyword
                        break
            
            if distress_detected:
                break
        
        # Step 3: Advanced pattern matching for English emotional distress
        if not distress_detected:
            for pattern in DISTRESS_PATTERNS:
                if re.search(pattern, normalized_message, re.IGNORECASE):
                    distress_detected = True
                    detected_language = "english_advanced"
                    detected_keyword = "emotional_distress_pattern"
                    break
        
        # Step 4: If no distress detected, return False
        if not distress_detected:
            return False
        
        # Step 5: Distress detected - Fetch tourist details
        tourist = crud_tourist.get_tourist(db, tourist_id)
        if not tourist:
            # Log this case but don't raise error - tourist might not be registered
            # but we still want to attempt emergency processing
            tourist_name = f"Unknown Tourist ({tourist_id[:8]})"
        else:
            tourist_name = tourist.name
        
        # Step 6: Trigger panic alert via alert service
        # Create timestamp for the alert
        from datetime import datetime
        alert_timestamp = datetime.utcnow()
        
        # Add detected language and keyword to location data for context
        enhanced_location_data = {
            **location_data,
            "detection_method": "text_analysis",
            "detected_language": detected_language,
            "detected_keyword": detected_keyword,
            "original_message": text_message[:100]  # First 100 chars for context
        }
        
        # Broadcast real-time alert
        await alert_service.trigger_panic_alert(
            tourist_id=tourist_id,
            name=tourist_name,
            location=enhanced_location_data,
            timestamp=alert_timestamp
        )
        
        # Step 7: Log to tamper-evident ledger
        ledger_service.log_panic_event_to_ledger(
            db=db,
            tourist_id=tourist_id,
            location_data=enhanced_location_data
        )
        
        # Step 8: Return True indicating successful distress detection and processing
        return True
        
    except Exception as e:
        # Log the error but don't raise it - we want to return False for processing errors
        # In production, this should be logged to a monitoring system
        print(f"Error processing text alert: {str(e)}")
        return False


def analyze_message_content(text_message: str) -> Dict[str, any]:
    """
    Analyze message content and return detailed analysis results
    
    This function provides detailed analysis of the text message including
    detected languages, keywords, confidence levels, and recommendations.
    
    Args:
        text_message: The text message to analyze
        
    Returns:
        Dict with analysis results including detected keywords and confidence
        
    Example:
        >>> result = analyze_message_content("मदद करो")
        >>> print(result['detected_languages'])  # ['hindi']
        >>> print(result['confidence'])  # 'high'
    """
    analysis = {
        "detected_languages": [],
        "detected_keywords": [],
        "confidence": "none",
        "is_distress": False,
        "recommendations": []
    }
    
    normalized_message = text_message.lower().strip()
    
    # Check each language
    for language, keywords in DISTRESS_KEYWORDS.items():
        for keyword in keywords:
            if language == "english":
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, normalized_message):
                    analysis["detected_languages"].append(language)
                    analysis["detected_keywords"].append(keyword)
                    analysis["is_distress"] = True
            else:
                if keyword in text_message:
                    analysis["detected_languages"].append(language)
                    analysis["detected_keywords"].append(keyword)
                    analysis["is_distress"] = True
    
    # Set confidence level
    if len(analysis["detected_keywords"]) > 0:
        if len(analysis["detected_keywords"]) >= 2:
            analysis["confidence"] = "high"
            analysis["recommendations"] = ["immediate_response", "contact_emergency_services"]
        else:
            analysis["confidence"] = "medium"
            analysis["recommendations"] = ["verify_situation", "prepare_response"]
    
    # Remove duplicates
    analysis["detected_languages"] = list(set(analysis["detected_languages"]))
    analysis["detected_keywords"] = list(set(analysis["detected_keywords"]))
    
    return analysis


def get_supported_languages() -> List[str]:
    """
    Get list of supported languages for distress detection
    
    Returns:
        List[str]: List of supported language names
    """
    return list(DISTRESS_KEYWORDS.keys())


def get_distress_keywords_for_language(language: str) -> Optional[List[str]]:
    """
    Get distress keywords for a specific language
    
    Args:
        language: Language name (e.g., 'hindi', 'english')
        
    Returns:
        Optional[List[str]]: List of keywords or None if language not supported
    """
    return DISTRESS_KEYWORDS.get(language.lower())
