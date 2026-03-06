import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from ..db import models


def hash_string(string: str) -> str:
    """
    Helper function to generate SHA-256 hash of a string
    
    Args:
        string: The string to hash
        
    Returns:
        The SHA-256 hexdigest of the encoded string
    """
    return hashlib.sha256(string.encode('utf-8')).hexdigest()


def get_latest_block_hash(db: Session) -> str:
    """
    Retrieves the hash of the latest block in the ledger
    
    Args:
        db: Database session
        
    Returns:
        The current_hash of the latest block, or genesis hash if no blocks exist
    """
    latest_block = db.query(models.IDLedger).order_by(models.IDLedger.id.desc()).first()
    
    if latest_block is None:
        # Return genesis hash - string of 64 zeros for the first block
        return '0' * 64
    else:
        return latest_block.current_hash


def add_new_block(db: Session, tourist_id: str, event_data: dict) -> models.IDLedger:
    """
    Creates and adds a new block to the tamper-evident ledger
    
    Args:
        db: Database session
        tourist_id: UUID string of the tourist
        event_data: Dictionary containing the event data to be recorded
        
    Returns:
        The newly created IDLedger block object
    """
    # Step 1: Get the previous block's hash
    previous_hash = get_latest_block_hash(db)
    
    # Step 2: Get current UTC timestamp
    timestamp = datetime.utcnow()
    
    # Step 3: Create deterministic string from block data
    # This MUST be deterministic for verification to work
    data_to_hash_string = f"{tourist_id}{timestamp.isoformat()}{json.dumps(event_data, sort_keys=True)}"
    
    # Step 4: Calculate the new block's hash
    # Hash = SHA-256(previous_hash + current_block_data)
    current_hash = hash_string(f"{previous_hash}{data_to_hash_string}")
    
    # Step 5: Create new IDLedger object
    new_block = models.IDLedger(
        tourist_id=tourist_id,
        timestamp=timestamp,
        data=event_data,
        previous_hash=previous_hash,
        current_hash=current_hash
    )
    
    # Step 6: Add, commit, and refresh the new block
    db.add(new_block)
    db.commit()
    db.refresh(new_block)
    
    # Step 7: Return the newly created block
    return new_block


def log_panic_event_to_ledger(db: Session, tourist_id: str, location_data: dict):
    """
    Logs a panic alert event to the tamper-evident ledger
    
    This function creates a standardized panic event entry and adds it to the ledger
    using the existing add_new_block function. This ensures critical panic incidents
    are immutably recorded with a verifiable audit trail.
    
    Args:
        db: Database session
        tourist_id: UUID string of the tourist who triggered the panic alert
        location_data: Dictionary containing location information with keys like
                      'latitude', 'longitude', and 'timestamp'
    
    Returns:
        None - This function's purpose is to log the event, not return data
    """
    # Create standardized event data for panic alerts
    event_data = {
        "event": "PANIC_ALERT",
        "details": "Panic button activated by tourist.",
        "location": location_data
    }
    
    # Use existing add_new_block function to create and save the ledger entry
    add_new_block(db=db, tourist_id=tourist_id, event_data=event_data)


def log_anomaly_event_to_ledger(db: Session, tourist_id: str, anomaly_details: dict):
    """
    Logs an AI-detected anomaly event to the tamper-evident ledger
    
    This function creates a standardized anomaly event entry and adds it to the ledger
    using the existing add_new_block function. This ensures AI-detected anomalies
    are immutably recorded with a verifiable audit trail for investigation purposes.
    
    Args:
        db: Database session
        tourist_id: UUID string of the tourist associated with the anomaly
        anomaly_details: Dictionary containing anomaly information provided by the AI service
                        Example: {"type": "INACTIVITY", "duration": "35 minutes", "last_seen": "2025-09-15T10:00:00Z"}
    
    Returns:
        None - This function's purpose is to log the event, not return data
    
    Usage Example:
        # Called by Developer 3 (AI Monitoring Service)
        log_anomaly_event_to_ledger(
            db=db,
            tourist_id="987fcdeb-51d4-43e8-9f12-345678901234",
            anomaly_details={
                "type": "INACTIVITY",
                "duration": "35 minutes",
                "last_seen": "2025-09-15T10:00:00Z",
                "confidence_score": 0.95,
                "analysis_method": "movement_pattern_analysis"
            }
        )
    """
    # Create standardized event data for AI anomaly detection
    event_data = {
        "event": "AI_ANOMALY_DETECTED",
        "details": anomaly_details  # Pass through the AI-provided details
    }
    
    # Use existing add_new_block function to create and save the ledger entry
    add_new_block(db=db, tourist_id=tourist_id, event_data=event_data)


def verify_chain(db: Session) -> bool:
    """
    Verifies the integrity of the entire blockchain ledger
    
    Args:
        db: Database session
        
    Returns:
        True if the chain is valid, False if tampering is detected
    """
    # Query all blocks ordered by ID (chronological order)
    all_blocks = db.query(models.IDLedger).order_by(models.IDLedger.id.asc()).all()
    
    # Initialize with genesis hash
    last_verified_hash = '0' * 64
    
    # Verify each block in sequence
    for block in all_blocks:
        # Recreate the deterministic data string using the same logic as add_new_block
        data_to_hash_string = f"{block.tourist_id}{block.timestamp.isoformat()}{json.dumps(block.data, sort_keys=True)}"
        
        # Recalculate what the hash should be
        recalculated_hash = hash_string(f"{last_verified_hash}{data_to_hash_string}")
        
        # Compare with stored hash
        if recalculated_hash != block.current_hash:
            # Tampering detected!
            return False
        
        # Verify that the previous_hash field matches what we expect
        if block.previous_hash != last_verified_hash:
            # Chain linkage broken!
            return False
        
        # Update for next iteration
        last_verified_hash = block.current_hash
    
    # If we get here, the entire chain is valid
    return True
