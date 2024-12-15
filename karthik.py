"""
Spam Detection System with OS Operations
This module provides a complete spam detection system with OS operations.
"""

import os
import sys
import json
import shutil
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict

# Constants
SPAM_INDICATORS = [
    'urgent', 'winner', 'prize', 'reward', 'claim', 'selected',
    'valued customer', 'call now', 'limited time', 'congratulations',
    'account compromised', 'security alert'
]

@dataclass
class DetectionResult:
    """Class to hold spam detection results."""
    classification: str
    score: int

class SystemManager:
    """Handles system operations and environment setup."""
    
    @staticmethod
    def get_system_info() -> Dict:
        """Get system information."""
        return {
            "os_name": os.name,
            "platform": sys.platform,
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "user": os.getenv("USER", "unknown")
        }
    
    @staticmethod
    def setup_environment() -> None:
        """Setup the working environment."""
        required_dirs = ["data", "data/input", "data/output", "data/logs"]
        for directory in required_dirs:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def cleanup_old_files(directory: str, days: int = 7) -> None:
        """Clean up files older than specified days."""
        current_time = datetime.now().timestamp()
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if current_time - os.path.getmtime(file_path) > days * 86400:
                    os.remove(file_path)

class SpamDetector:
    """Main class for spam detection."""
    
    def __init__(self, spam_threshold: int = 2):
        self.spam_threshold = spam_threshold
    
    def calculate_spam_score(self, text: str) -> int:
        """Calculate spam score based on various indicators."""
        score = 0
        
        # Check for spam indicators
        for indicator in SPAM_INDICATORS:
            if indicator.lower() in text.lower():
                score += 1
        
        # Check for excessive punctuation
        if text.count('!') > 2:
            score += 1
        
        # Check for ALL CAPS words
        caps_words = [word for word in text.split() 
                     if len(word) > 2 and word.isupper()]
        if len(caps_words) > 2:
            score += 1
            
        return score
    
    def classify(self, text: str) -> DetectionResult:
        """Classify text as spam or not spam."""
        score = self.calculate_spam_score(text)
        classification = "SPAM" if score >= self.spam_threshold else "NOT SPAM"
        return DetectionResult(classification=classification, score=score)

class FileProcessor:
    """Handles file operations with OS integration."""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.input_dir = os.path.join(base_dir, "input")
        self.output_dir = os.path.join(base_dir, "output")
        self.logs_dir = os.path.join(base_dir, "logs")
    
    def save_result(self, message: str, result: DetectionResult) -> str:
        """Save detection result to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        data = {
            "timestamp": timestamp,
            "message": message,
            "classification": result.classification,
            "score": result.score
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def log_operation(self, operation: str, details: str) -> None:
        """Log system operations."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(self.logs_dir, "system_log.txt")
        
        log_entry = (
            f"[{timestamp}] {operation}\n"
            f"Details: {details}\n"
            f"{'-' * 50}\n"
        )
        
        with open(log_file, "a") as f:
            f.write(log_entry)
    
    def backup_data(self) -> str:
        """Create a backup of the data directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup_{timestamp}"
        shutil.make_archive(backup_dir, 'zip', self.base_dir)
        return f"{backup_dir}.zip"

def main():
    """Main function to run the spam detection system."""
    try:
        # Initialize system
        system_manager = SystemManager()
        system_info = system_manager.get_system_info()
        print("System Information:")
        for key, value in system_info.items():
            print(f"- {key}: {value}")
        
        # Setup environment
        print("\nSetting up environment...")
        system_manager.setup_environment()
        
        # Initialize components
        detector = SpamDetector()
        file_processor = FileProcessor()
        
        # Create test messages
        test_messages = [
            "call you later",
            "Hey, are we still on for lunch today?",
            "Urgent! Your account has been compromised. Reply now to secure it.",
            "Hi, just checking in to see how you're doing.",
            "I HAVE A DATE ON SUNDAY WITH WILL!!",
            "WINNER!! As a valued network customer you have been selected to receive a £900 prize reward!"
        ]
        
        # Process messages
        print("\nProcessing messages...")
        results = []
        for message in test_messages:
            result = detector.classify(message)
            file_processor.save_result(message, result)
            file_processor.log_operation("Message Classification", 
                                      f"Message: {message}\nResult: {result}")
            results.append(result)
        
        # Create backup
        backup_file = file_processor.backup_data()
        print(f"\nBackup created: {backup_file}")
        
        # Cleanup old files
        system_manager.cleanup_old_files("data/output", days=7)
        
        # Display summary
        spam_count = sum(1 for r in results if r.classification == "SPAM")
        print("\nResults Summary:")
        print(f"- Total messages: {len(results)}")
        print(f"- Spam messages: {spam_count}")
        print(f"- Ham messages: {len(results) - spam_count}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
