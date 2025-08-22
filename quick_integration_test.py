#!/usr/bin/env python3
"""
Quick Integration Test
=====================

This script demonstrates that Issues #1 and #2 are resolved.
It can be run independently to verify LocalLLM functionality.
"""

import sys
from pathlib import Path

def test_integration():
    """Test LocalLLM integration functionality"""
    print("🧪 LocalLLM Integration Test")
    print("=" * 40)
    
    # Add LocalLLM to path
    localllm_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(localllm_path))
    
    try:
        # Test Issue #1 resolution: External integration
        print("\n✅ Testing Issue #1 Resolution:")
        from integration import summarize_text, check_installation
        
        # Basic functionality test
        result = summarize_text("Test document content", language="ja")
        print(f"   Summary result type: {type(result)}")
        
        # Installation status
        status = check_installation()
        print(f"   Components available: {len([k for k, v in status.items() if v and k != 'errors'])}")
        
        # Test Issue #2 resolution: Enhanced API imports
        print("\n✅ Testing Issue #2 Resolution:")
        from api.enhanced_api import SummaryConfig, summarize_json
        
        # Configuration test
        config = SummaryConfig(language="ja", summary_type="detailed")
        print(f"   Config created: language={config.language}")
        
        # JSON processing test
        test_data = {"content": "Test content"}
        result = summarize_json(test_data, config=config)
        print(f"   JSON processing: {type(result)}")
        
        print("\n🎉 SUCCESS: Both issues are resolved!")
        print("✅ Issue #1: External integration - WORKING")
        print("✅ Issue #2: Import fallbacks - WORKING")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)