# -*- coding: utf-8 -*-
"""
CPSC 599 module: src.languages.english_canadian

Purpose
=======
 Contains a collection of rules to apply to phonemes.
 
Language
========
 This file applies to Canadian English.
 
Usage
=====
 All functions declared in this module for external iteration must have the
 following input signature:
  - B{C{ipa_character}} (unicode) - The character, representative of a phoneme,
    being processed.
  - B{C{preceding_phonemes}} (sequence) - A collection of all phonemes, in order,
    that precede the current IPA character in the current word.
  - B{C{following_phonemes}} (sequence) - A collection of all phonemes, in order,
    that follow the current IPA character in the current word.
  - B{C{word_position}} (int) - The current word's position in its sentence,
    indexed from 1.
  - B{C{remaining_words}} (int) - The number of words remaining before the end of
    the sentence is reached, not including the current word.
  - B{C{previous_words}} (sequence) - A collection of all words that have been
    previously synthesized.
  - B{C{following_words}} (sequence) - A collection of all words that have yet to
    be synthesized.
  - B{C{sentence_position}} (int) - The current sentence's position in its
    paragraph, indexed from 1.
  - B{C{remaining_sentences}} (int) - The number of sentences remaining before
    the end of the paragraph is reached, not including the current sentence.
  - B{C{is_quoted}} (bool) - True if the current word is part of a quoted body.
  - B{C{is_emphasized}} (bool) - True if the current word is part of an
    emphasized body.
  - B{C{is_content}} (bool) - True if the current word was marked as a content
    word.
  - B{C{is_question}} (bool) - True if the current sentence ends with a question
    mark.
  - B{C{is_exclamation}} (bool) - True if the current sentence ends with an
    exclamation mark.
  - B{C{previous_phoneme_parameters}} (list) - A collection of all parameters that
    appear as part of this phoneme, prior to the parameter-set currently being
    manipulated.
  - B{C{remaining_phoneme_parameter_count}} (int) - The number of parameter-sets
    yet to be processed as part of this phoneme.
  - B{C{previous_sound_parameters}} (list) - A list of all preceding
    parameter-sets introduced prior to the current paramter-set by language
    rules.
  - B{C{following_sound_parameters}} (list) - A list of all preceding
    parameter-sets introduced after to the current paramter-set by language
    rules.
  - B{C{parameters}} (list(33)) - A collection of parameters associated with the
    sound currently being procesed.
 
 Additionally, they must have the following return format:
  - B{tuple(3)} - A list of parameter-sets that precede this sound, a list of
    parameter-sets that follow this sound, and an f0 multiplier.
 
 All functions may modify the input parameter-set, C{parameters}.
 
 To enable use of a function you have defined, you must add a reference to the
 RULE_FUNCTIONS tuple, found at the end of this file. 
 
Legal
=====
 All code, unless otherwise indicated, is original, and subject to the
 terms of the GPLv3, which is provided in COPYING.
 
 (C) Neil Tallim, Sydni Bennie, 2009
"""
import src.ipa as ipa

NAME = "Canadian English"

_QUESTION_WORDS = (u'hæw', u'hu', u'hum', u'\u028d\u025b\u0279', u'\u028d\u0259t', u'\u028d\u025bn' u'\u028d\u028cj') #: A collection of known question-words. (Unicode-values: where, what, when, why)

def _amplifyContent(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Increases the emphasis placed on a word identified as content-bearing in a
	sentence.
	
	@author: Sydni Bennie
	"""
	if is_content and not ipa_character == u'\u0259':
		parameters[5] *= 1.25 #Boost f1.
		if ipa_character in ipa.VOWELS:
			parameters[32] *= 1.1 #Increase duration, just a little.
			return ([], [], 0.95) #Increase pitch, just a little.
	return ([], [], 1.0)
	
def _degradePitch(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Lowers the pitch exponentially over the course of a spoken sentence.
	
	@author: Sydni Bennie
	"""
	if not is_question:
		decay_ratio = 1.0 - (0.05 / (word_position + remaining_words))
		return ([], [], 1.0 / (decay_ratio ** word_position))
	return ([], [], 1.0)
	
def _emphasizeSpeech(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Raises the pitch and volume of bolded speech while lengthening its duration.
	
	@author: Sydni Bennie
	"""
	if is_emphasized and ipa_character not in ipa.STOPS:
		parameters[27] += 5 #Boost bypass gain.
		parameters[32] *= 1.1 #Increase duration.
		return ([], [], 0.95) #Increase pitch, sligthly.
	return ([], [], 1.0)
	
def _exclaim(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Slightly decreases the duration of phonemes and increases amplitude.
	
	In the event of a question or a terminal nucleus, pitch is also increased.
	
	@author: Sydni Bennie
	"""
	if is_exclamation:
		#Increase bandwidths 1-3.
		parameters[16] *= 1.1
		parameters[17] *= 1.1
		parameters[18] *= 1.1
		
		#Raise voicing amplitudes by 5.
		parameters[30] = min(parameters[30] + 5, 60)
		parameters[31] = min(parameters[31] + 5, 60)
		
		parameters[32] *= 0.95 #Decrease duration.
		
		if is_question:
			return ([], [], 0.95) #Increase pitch.
		elif ipa_character in ipa.VOWELS and not [c for c in following_phonemes if c in ipa.VOWELS]: #Last syllable.
			parameters[32] *= 1.35 #Increase duration
			return ([], [], 0.95) #Increase pitch.
			
	return ([], [], 0.975) #Increase pitch, sligthly.
	
def _inflectQuestionPitch(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Changes the pitch at the end of a question-sentence, rising in most cases,
	and falling in the case of a 'wh' question.
	
	@author: Sydni Bennie
	"""
	if is_question and not ipa_character == u'\u0259' and ipa_character in ipa.VOWELS: #No schwas allowed.
		if remaining_words <= 2: #Ignore questions and early positions in sentences.
			if previous_words and [p_w for p_w in previous_words if p_w in _QUESTION_WORDS]:
				if remaining_words == 2 and following_words[0] == u'\u028c': #Also a wedge. Time backwards-goes.
					return ([], [], 0.7)  #Raise pitch on the second-last word.
				elif remaining_words == 1 and not following_phonemes and not preceding_phonemes and not ipa_character == u'\u028c': #Wedge.
					return ([], [], 0.8) #Raise pitch on the second-last word.
				return ([], [], 0.9) #Raise pitch very slightly on the last word.
				
		if remaining_words == 0:
			position = len([p for p in preceding_phonemes if p in ipa.VOWELS])
			rise_ratio = 1.0 - (0.11 / (position + len([p for p in following_phonemes if p in ipa.VOWELS]) + 1))
			return ([], [], (-0.05 + rise_ratio ** position))
			
		word = u''.join(preceding_phonemes + [ipa_character] + following_phonemes)
		if word in _QUESTION_WORDS and not [p_w for p_w in previous_words if p_w in _QUESTION_WORDS]:
			return ([], [], 0.9) #Increase pitch.
	return ([], [], 1.0)
	
def _lengthenTerminal(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Lengthens the duration of each vowel in the final word of a sentence.
	
	@author: Sydni Bennie
	"""
	if remaining_words == 0 and not ipa_character == u'\u0259' and ipa_character in ipa.VOWELS:
		parameters[32] *= 1.5 #Increase duration.
	return ([], [], 1.0)
	
def _liquidateVowels(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Extends the sound of a liquid when it is immediately followed by a vowel.
	
	@author: Sydni Bennie
	"""
	if remaining_phoneme_parameter_count == 0 and following_phonemes and ipa_character in ipa.LIQUIDS and following_phonemes[0] in ipa.VOWELS:
		vowel_values = ipa.IPA_PARAMETERS[following_phonemes[0]]
		values = zip(parameters[:32], vowel_values[:32])
		return ([], [[(l + v * 2) / 3 for (l, v) in values] + [int(vowel_values[32] * 0.25)]], 1.0) #Compensate for universal blending; add 50% of both sounds for 25% of the vowel's length.
	return ([], [], 1.0)
	
def _quoteSpeech(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Raises the pitch and volume of quoted speech while shortening its duration.
	
	@author: Sydni Bennie
	"""
	if is_quoted:
		parameters[27] += 5 #Boost bypass gain.
		parameters[32] *= 0.925 #Reduce duration.
		return ([], [], 0.975) #Increase pitch.
	return ([], [], 1.0)
	
def _shortenDipthong(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, previous_phoneme_parameters, remaining_phoneme_parameter_count, previous_sound_parameters, following_sound_parameters, parameters):
	"""
	Reduces the length of a vowel that immediately follows another vowel in a
	word.
	
	@author: Sydni Bennie
	"""
	if preceding_phonemes and ipa_character in ipa.VOWELS and preceding_phonemes[-1] in ipa.VOWELS:
		parameters[32] *= 0.5 #Reduce duration.
	return ([], [], 1.0)
	
	
RULE_FUNCTIONS = (
 _liquidateVowels,
 _inflectQuestionPitch,
 _amplifyContent,
 _emphasizeSpeech,
 _quoteSpeech,
 _degradePitch,
 _lengthenTerminal,
 _shortenDipthong,
 _exclaim,
) #: A collection of all functions to call, in order, to apply this language's rules. 
