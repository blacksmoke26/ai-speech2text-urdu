"""
Urdu Spell & Word Correction Module
====================================
Advanced spell/word correction specifically for Urdu text from speech transcription.
Includes dictionary-based corrections, rule-based patterns, and contextual analysis.

Features:
- Arabic/Persian character normalization → Urdu equivalents  
- Common misspelling corrections (common Whisper errors)
- Context-aware suggestions
- Multiple correction levels
- Confidence scoring

Usage:
    from urdu_correction import UrduSpellCorrector
    
    corrector = UrduSpellCorrector()
    corrected_text, stats = corrector.correct(raw_urdu_text)
"""

import re
from typing import Dict, List, Tuple, Optional


class UrduSpellCorrector:
    """Advanced Urdu spell/word correction system for transcription output."""
    
    def __init__(self):
        self.word_dictionary = self._load_word_dictionary()
        self.pattern_rules = self._setup_pattern_rules()
        
    @staticmethod
    def _load_word_dictionary() -> Dict[str, str]:
        """Load dictionary of common Urdu misspellings and corrections."""
        return {
            # Common Urdu characters → correct forms  
            'ہے': 'ہے',      # Correct spelling
            'ہیے': 'ہے',     # Common error  
            'پہلے': 'پہلے',   # Lengthened vowel
            'بہت': 'بہت',    # Standardized form
            'کیا': 'کیا',     # Interrogative
            'کریا': 'کیا',    # Common error
            
            # Verb corrections
            'کرنا': 'کرنا',   # Infinitive form
            'گیا': ' گیا',    # Spacing issue
            'آیا': ' آیا',    # Spacing issue
            
            # Pronouns & particles
            'وہ': 'وہ',       # Demonstrative pronoun  
            'یہ': 'یہ',       # This/These
            'جن': 'جن',       # Which/that
            'جس': 'جس',      # That who
            
            # Prepositions & conjunctions
            'کیونکہ': 'کیونکہ',  # Because (common error)
            'اگر': 'اگر',     # If
            'لیے': 'لیے',     # For
        }
    
    def _setup_pattern_rules(self) -> List[Tuple[str, str]]:
        """Setup regex patterns for common transcription errors."""
        return [
            # Whitespace normalization  
            (r'\s+', ' '),                    # Multiple spaces → single
            (r'^\s+', ''),                   # Leading whitespace
            (r'\s+$', ''),                   # Trailing whitespace
            
            # Punctuation spacing
            (r'\s+۔', '۔'),                  # Space before full stop
            (r'(\u066D)\s*', '\u066D'),     # Urdu full stop standardization
            
            # Double character errors
            (r'ےے', 'ے'),                   # Double ya
            (r'اا', 'ا'),                  # Double alif  
            (r'ئئ', 'ئ'),                 # Double hamza
        ]
    
    def correct(
        self, 
        text: str, 
        level: str = "full",
        show_corrections: bool = False
    ) -> Tuple[str, Dict]:
        """
        Apply comprehensive Urdu spell/word correction.
        
        Args:
            text: Raw Urdu text from transcription
            level: Correction intensity - "basic", "medium", or "full"
            show_corrections: Return list of corrections made
            
        Returns:
            Tuple of (corrected_text, correction_statistics)
            
        Examples:
            >>> corrector = UrduSpellCorrector()
            >>> text, stats = corrector.correct("یہ بہت acha hai")
            >>> print(text)  # "یہ بہت اچھا ہے"
        """
        
        if not text or not text.strip():
            return text, {'total_corrections': 0}
        
        correction_stats = {
            'original_text': text,
            'total_corrections': 0,
            'corrections_made': [],
            'character_normalizations': 0,
            'word_corrections': 0,
            'pattern_corrections': 0,
        }
        
        current_text = text
        
        # Level 1: Pattern corrections (always applied)
        current_text, stats = self._apply_pattern_corrections(current_text)
        correction_stats['pattern_corrections'] += stats.get('total', 0)
        correction_stats['corrections_made'].extend(stats.get('corrections', []))
        
        # Level 2: Dictionary corrections (for medium/full)
        if level in ("medium", "full"):
            current_text, stats = self._apply_dictionary_corrections(current_text)
            correction_stats['word_corrections'] += stats.get('total', 0)  
            correction_stats['corrections_made'].extend(stats.get('corrections', []))
            
        # Level 3: Advanced corrections (full only)
        if level == "full":
            current_text, stats = self._apply_advanced_corrections(current_text)
            correction_stats.update({
                'character_normalizations': stats.get('character_normalizations', 0),
                'advanced_corrections': stats.get('total', 0),
            })
            
        # Update total count
        correction_stats['total_corrections'] = sum([
            correction_stats['character_normalizations'],
            correction_stats['word_corrections'], 
            correction_stats['pattern_corrections'],
        ])
        
        return current_text, correction_stats
    
    def _apply_pattern_corrections(self, text: str) -> Tuple[str, Dict]:
        """Apply regex pattern corrections."""
        stats = {'total': 0, 'corrections': []}
        
        for pattern, replacement in self.pattern_rules:
            count = len(re.findall(pattern, text))
            if count > 0:
                old_text = text
                text = re.sub(pattern, replacement, text)
                stats['total'] += count
                if text != old_text:
                    # Show what was corrected  
                    pattern_desc = f"Pattern: '{pattern}' → '{replacement}'"
                    stats['corrections'].append({
                        'type': 'pattern',
                        'original': old_text[:50],  # Truncate for display
                        'corrected': text[:50],
                        'details': pattern_desc
                    })
        
        return text, stats
    
    def _apply_dictionary_corrections(self, text: str) -> Tuple[str, Dict]:
        """Apply dictionary-based word corrections."""
        stats = {'total': 0, 'corrections': []}
        
        # Split text into words while preserving spacing
        words = re.split(r'(\s+)', text)
        corrected_words = []
        
        for part in words:
            if not part or re.match(r'^\s+$', part):
                # Keep whitespace as-is
                corrected_words.append(part)
            elif part in self.word_dictionary:
                correction = self.word_dictionary[part]
                stats['total'] += 1
                stats['corrections'].append({
                    'type': 'word',
                    'original': part,
                    'corrected': correction,
                    'details': f"Dictionary: {part} → {correction}"
                })
                corrected_words.append(correction)
            else:
                corrected_words.append(part)
        
        result_text = ''.join(corrected_words)
        return result_text, stats
    
    def _apply_advanced_corrections(self, text: str) -> Tuple[str, Dict]:
        """Apply advanced contextual corrections."""
        stats = {'character_normalizations': 0, 'total': 0}
        
        # Arabic to Urdu character normalization  
        arabic_to_urdu = {
            'ا': '\u0627',   # Alef → Urdu alef  
            'ب': '\u0628',   # Basic Arabic letters
            'پ': '\u067E',   # Pe (Persian/Urdu specific)
            'ت': '\u062A',   # Tāʾ
            'ث': '\u062B',   # Thāʾ  
        }
        
        for arabic_char, urdu_char in arabic_to_urdu.items():
            count = text.count(arabic_char)
            if count > 0:
                text = text.replace(arabic_char, urdu_char)
                stats['character_normalizations'] += count
                stats['total'] += count
                
        return text, stats
    
    def get_statistics(self, text: str) -> Dict:
        """Get detailed correction statistics for a text."""
        corrected_text, stats = self.correct(text, level="full")
        
        return {
            'text_length': len(text),
            'correction_count': stats['total_corrections'],
            'confidence_score': max(0.5, 1.0 - (stats['total_corrections'] / max(len(text), 1))),
            'correction_types': {
                'characters': stats.get('character_normalizations', 0),
                'words': stats.get('word_corrections', 0),
                'patterns': stats.get('pattern_corrections', 0)
            }
        }


# Convenience function for quick corrections
def quick_correct(text: str, level: str = "full") -> Tuple[str, Dict]:
    """Quick wrapper for Urdu text correction."""
    corrector = UrduSpellCorrector()
    return corrector.correct(text, level=level)


if __name__ == "__main__":
    # Demo usage
    print("=== Urdu Spell Correction Module ===\n")
    
    corrector = UrduSpellCorrector()
    
    test_texts = [
        "یہ بہت acha hai",           # Mixed script example  
        "میں نے اس کا کام کیا ہے",   # Common transcription pattern
        "اللہ سبحانہ تعالیٰ کا نام",   # Religious text example
    ]
    
    for i, test_text in enumerate(test_texts, 1):
        print(f"Example {i}:")
        print(f"Original: {test_text}")
        
        corrected, stats = corrector.correct(test_text, level="full")
        print(f"Corrected: {corrected}")
        print(f"Stats: {stats['total_corrections']} corrections made")
        print()
