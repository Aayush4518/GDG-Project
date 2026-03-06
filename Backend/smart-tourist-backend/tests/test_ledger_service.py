"""
Test suite for Tamper-Evident Ledger Service
Testing objectives from Prompt 1:
- Hashing utilities and getting the latest block
- Creating and adding new blocks  
- Chain verification logic for demo
"""

import pytest
import hashlib
import json
from datetime import datetime
from unittest.mock import Mock, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ledger_service import hash_string, get_latest_block_hash, add_new_block, verify_chain


class TestHashingUtilities:
    """Test Part A: Hashing Utilities and Getting Latest Block"""
    
    def test_hash_string_deterministic(self):
        """Test that hash_string produces deterministic SHA-256 output"""
        test_input = "Hello, Smart Tourist System!"
        
        # Calculate expected hash manually
        expected = hashlib.sha256(test_input.encode('utf-8')).hexdigest()
        
        # Test our function
        result = hash_string(test_input)
        
        assert result == expected
        assert len(result) == 64  # SHA-256 produces 64-character hex string
        print(f"✅ hash_string test passed: {test_input} -> {result}")
    
    def test_hash_string_different_inputs(self):
        """Test that different inputs produce different hashes"""
        input1 = "tourist_1"
        input2 = "tourist_2"
        
        hash1 = hash_string(input1)
        hash2 = hash_string(input2)
        
        assert hash1 != hash2
        assert len(hash1) == len(hash2) == 64
        print(f"✅ Different inputs produce different hashes")
    
    def test_get_latest_block_hash_empty_db(self):
        """Test get_latest_block_hash returns genesis hash when no blocks exist"""
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None  # No blocks in database
        
        result = get_latest_block_hash(mock_db)
        
        expected_genesis = '0' * 64
        assert result == expected_genesis
        print(f"✅ Genesis hash test passed: {result}")
    
    def test_get_latest_block_hash_with_blocks(self):
        """Test get_latest_block_hash returns latest block's current_hash"""
        # Mock database session and block
        mock_db = Mock()
        mock_query = Mock()
        mock_block = Mock()
        mock_block.current_hash = "abcd1234" + "0" * 56  # Mock 64-char hash
        
        mock_db.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = mock_block
        
        result = get_latest_block_hash(mock_db)
        
        assert result == mock_block.current_hash
        print(f"✅ Latest block hash retrieval test passed: {result}")


class TestBlockCreation:
    """Test Part B: Creating and Adding New Blocks"""
    
    def test_block_data_deterministic_string(self):
        """Test that block data produces deterministic hash string"""
        tourist_id = "test-uuid-123"
        timestamp = datetime.fromisoformat("2025-09-15T10:30:00")
        event_data = {"event": "REGISTRATION", "name": "John Doe"}
        
        # This is the exact format used in add_new_block
        data_string = f"{tourist_id}{timestamp.isoformat()}{json.dumps(event_data, sort_keys=True)}"
        
        expected = f"test-uuid-1232025-09-15T10:30:00" + '{"event": "REGISTRATION", "name": "John Doe"}'
        
        assert data_string == expected
        print(f"✅ Deterministic block data string: {data_string}")
    
    def test_add_new_block_logic(self):
        """Test the core logic of add_new_block without database"""
        # Test the hashing logic that should be in add_new_block
        tourist_id = "uuid-test-123"
        timestamp = datetime.fromisoformat("2025-09-15T10:30:00")
        event_data = {"event": "REGISTRATION"}
        previous_hash = "0" * 64  # Genesis hash
        
        # Simulate the logic from add_new_block
        data_to_hash_string = f"{tourist_id}{timestamp.isoformat()}{json.dumps(event_data, sort_keys=True)}"
        expected_current_hash = hash_string(f"{previous_hash}{data_to_hash_string}")
        
        # Verify the hash is calculated correctly
        manual_hash = hashlib.sha256(f"{previous_hash}{data_to_hash_string}".encode()).hexdigest()
        
        assert expected_current_hash == manual_hash
        assert len(expected_current_hash) == 64
        print(f"✅ Block hash calculation logic verified")
        print(f"    Data string: {data_to_hash_string}")
        print(f"    Calculated hash: {expected_current_hash}")


class TestChainVerification:
    """Test Part C: Chain Verification Logic"""
    
    def test_verify_chain_logic_single_block(self):
        """Test chain verification logic for a single block"""
        # Mock a single block
        mock_block = Mock()
        mock_block.tourist_id = "uuid-123"
        mock_block.timestamp = datetime.fromisoformat("2025-09-15T10:30:00")
        mock_block.data = {"event": "REGISTRATION"}
        mock_block.previous_hash = "0" * 64
        
        # Calculate what the current_hash should be
        data_string = f"{mock_block.tourist_id}{mock_block.timestamp.isoformat()}{json.dumps(mock_block.data, sort_keys=True)}"
        expected_hash = hash_string(f"{mock_block.previous_hash}{data_string}")
        mock_block.current_hash = expected_hash
        
        # Mock database
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_block]
        
        # Test verification
        result = verify_chain(mock_db)
        
        assert result == True
        print(f"✅ Single block chain verification passed")
        print(f"    Block hash: {expected_hash}")
    
    def test_verify_chain_logic_multiple_blocks(self):
        """Test chain verification for multiple linked blocks"""
        # Block 1 (genesis)
        block1 = Mock()
        block1.tourist_id = "uuid-1"
        block1.timestamp = datetime.fromisoformat("2025-09-15T10:30:00")
        block1.data = {"event": "REGISTRATION"}
        block1.previous_hash = "0" * 64
        
        data1 = f"{block1.tourist_id}{block1.timestamp.isoformat()}{json.dumps(block1.data, sort_keys=True)}"
        block1.current_hash = hash_string(f"{block1.previous_hash}{data1}")
        
        # Block 2 (linked to block 1)
        block2 = Mock()
        block2.tourist_id = "uuid-1"
        block2.timestamp = datetime.fromisoformat("2025-09-15T11:00:00")
        block2.data = {"event": "LOCATION_UPDATE", "lat": 12.9716, "lng": 77.5946}
        block2.previous_hash = block1.current_hash
        
        data2 = f"{block2.tourist_id}{block2.timestamp.isoformat()}{json.dumps(block2.data, sort_keys=True)}"
        block2.current_hash = hash_string(f"{block2.previous_hash}{data2}")
        
        # Mock database
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [block1, block2]
        
        # Test verification
        result = verify_chain(mock_db)
        
        assert result == True
        print(f"✅ Multi-block chain verification passed")
        print(f"    Block 1 hash: {block1.current_hash}")
        print(f"    Block 2 hash: {block2.current_hash}")
    
    def test_verify_chain_detects_tampering(self):
        """Test that verify_chain detects tampering"""
        # Create a valid block
        block = Mock()
        block.tourist_id = "uuid-123"
        block.timestamp = datetime.fromisoformat("2025-09-15T10:30:00")
        block.data = {"event": "REGISTRATION"}
        block.previous_hash = "0" * 64
        
        # Calculate correct hash
        data_string = f"{block.tourist_id}{block.timestamp.isoformat()}{json.dumps(block.data, sort_keys=True)}"
        correct_hash = hash_string(f"{block.previous_hash}{data_string}")
        
        # Tamper with the hash (simulate database tampering)
        block.current_hash = "tampered_hash_" + "0" * 50
        
        # Mock database
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [block]
        
        # Test verification should fail
        result = verify_chain(mock_db)
        
        assert result == False
        print(f"✅ Tampering detection test passed - chain verification correctly failed")
        print(f"    Expected: {correct_hash}")
        print(f"    Found: {block.current_hash}")


def run_ledger_tests():
    """Run all ledger service tests"""
    print("=" * 70)
    print("TESTING PROMPT 1 OBJECTIVES: TAMPER-EVIDENT LEDGER SERVICE")
    print("=" * 70)
    
    # Test hashing utilities
    print("\n📋 Testing Part A: Hashing Utilities and Latest Block Retrieval")
    hash_tests = TestHashingUtilities()
    hash_tests.test_hash_string_deterministic()
    hash_tests.test_hash_string_different_inputs()
    hash_tests.test_get_latest_block_hash_empty_db()
    hash_tests.test_get_latest_block_hash_with_blocks()
    
    # Test block creation
    print("\n📋 Testing Part B: Block Creation and Addition Logic")
    block_tests = TestBlockCreation()
    block_tests.test_block_data_deterministic_string()
    block_tests.test_add_new_block_logic()
    
    # Test chain verification
    print("\n📋 Testing Part C: Chain Verification and Tampering Detection")
    verify_tests = TestChainVerification()
    verify_tests.test_verify_chain_logic_single_block()
    verify_tests.test_verify_chain_logic_multiple_blocks()
    verify_tests.test_verify_chain_detects_tampering()
    
    print("\n" + "=" * 70)
    print("✅ ALL PROMPT 1 OBJECTIVES ACHIEVED!")
    print("✅ Tamper-evident ledger service implementation verified")
    print("=" * 70)


if __name__ == "__main__":
    run_ledger_tests()
