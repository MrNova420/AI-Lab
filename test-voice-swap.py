#!/usr/bin/env python3
"""
Quick test script to swap voice systems
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from core.speech_integration import SpeechSystemManager, VoiceSystemBackup
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('VoiceTest')


def dummy_ai_model(user_text: str) -> str:
    """Dummy AI model for testing"""
    return f"You said: {user_text}. This is a test response from the AI."


def main():
    logger.info("=" * 80)
    logger.info("🎙️  VOICE SYSTEM SWAP TEST")
    logger.info("=" * 80)
    logger.info("")
    
    # Create backup first
    logger.info("📦 Step 1: Creating backup of current system...")
    VoiceSystemBackup.create_backup()
    logger.info("")
    
    # Initialize manager
    manager = SpeechSystemManager()
    
    # Test new system
    logger.info("🚀 Step 2: Loading NEW speech-ai-system...")
    logger.info("")
    
    if manager.use_new_speech_system():
        logger.info("")
        logger.info("✅ NEW SYSTEM LOADED!")
        logger.info("")
        logger.info("🎤 Step 3: Testing transcription...")
        logger.info("   Say something now (speak for 2-3 seconds then stop)...")
        logger.info("")
        
        text = manager.transcribe()
        
        if text:
            logger.info("")
            logger.info(f"✅ Transcription successful!")
            logger.info("")
            logger.info("🔊 Step 4: Testing text-to-speech...")
            manager.speak("The new speech system is working perfectly. This is a test of the high quality text to speech.")
            logger.info("")
            logger.info("✅ TTS successful!")
            logger.info("")
            logger.info("=" * 80)
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📝 SUMMARY:")
            logger.info("   ✓ Backup created")
            logger.info("   ✓ New system loaded")
            logger.info("   ✓ Speech-to-text working")
            logger.info("   ✓ Text-to-speech working")
            logger.info("")
            logger.info("💡 TO USE IN YOUR APP:")
            logger.info("   from core.speech_integration import SpeechSystemManager")
            logger.info("   manager = SpeechSystemManager()")
            logger.info("   manager.use_new_speech_system()")
            logger.info("")
            logger.info("💡 TO REVERT:")
            logger.info("   manager.use_old_voice_system()")
            logger.info("   # or")
            logger.info("   VoiceSystemBackup.restore_backup()")
            logger.info("")
        else:
            logger.error("❌ Transcription returned empty")
    else:
        logger.error("❌ Failed to load new system")
    
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("👋 Test cancelled by user")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        logger.exception("Full error:")
