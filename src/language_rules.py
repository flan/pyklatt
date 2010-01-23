# -*- coding: utf-8 -*-
"""
CPSC 599 module: src.language_rules

Purpose
=======
 Applies language-specific transformation rules to phonemes.
 
Legal
=====
 All code, unless otherwise indicated, is original, and subject to the
 terms of the GPLv3, which is provided in COPYING.
 
 (C) Neil Tallim, 2009
"""
#Change the following line to use other language rulesets.
import languages.english_canadian as language

def applyRules(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, parameters_list):
	"""
	Iterates through all parameters that make up the current phoneme, applying
	all applicable language-specific rules, in a specific order, to each
	parameter-set.
	
	The input list of parameters is not altered by this function.
	
	@type ipa_character: unicode
	@param ipa_character: The character, representative of a phoneme, being
	    processed.
	@type preceding_phonemes: sequence
	@param preceding_phonemes: A collection of all phonemes, in order, that
	    precede the current IPA character in the current word.
	@type following_phonemes: sequence
	@param following_phonemes: A collection of all phonemes, in order, that
	    follow the current IPA character in the current word.
	@type word_position: int
	@param word_position: The current word's position in its sentence, indexed
	    from 1.
	@type remaining_words: int
	@param remaining_words: The number of words remaining before the end of the
	    sentence is reached, not including the current word.
	@type previous_words: sequence
	@param previous_words: A collection of all words that have been previously
	    synthesized.
	@type following_words: sequence
	@param following_words: A collection of all words that have yet to be
	    synthesized.
	@type sentence_position: int
	@param sentence_position: The current sentence's position in its paragraph,
	    indexed from 1.
	@type remaining_sentences: int
	@param remaining_sentences: The number of sentences remaining before the end
	    of the paragraph is reached, not including the current sentence.
	@type is_quoted: bool
	@param is_quoted: True if the current word is part of a quoted body.
	@type is_emphasized: bool
	@param is_emphasized: True if the current word is part of an emphasized body.
	@type is_content: bool
	@param is_content: True if the current word was marked as a content word.
	@type is_question: bool
	@param is_question: True if the current sentence ends with a question mark.
	@type is_exclamation: bool
	@param is_exclamation: True if the current sentence ends with an exclamation
	    mark.
	@type parameters_list: list
	@param parameters_list: A collection of all sounds currently associated with
	    the phoneme being processed.
	
	@rtype: tuple(2)
	@return: An updated list of parameters, consisting of transformations of
	    the base sounds, plus anything added to the stream, and an equal-length
	    collection of f0 multiplier values, with higher numbers meaning
	    lower-pitched sounds.
	"""
	rule_functions = language.RULE_FUNCTIONS
	
	f0_multipliers = []
	transformed_parameters = []
	initial_parameter_count_zero = len(parameters_list) - 1
	for (i, parameters) in enumerate(parameters_list): #Transforms each parameter-set in the input-list, in order.
		parameters = parameters[:] #Make a local copy.
		f0_multiplier = 1.0
		preceding_parameters = []
		following_parameters = []
		for function in rule_functions: #Applies each language rule, in order. New parameters lists appear on either side of the central parameter set.
			(preceding_params, following_params, multiplier) = function(ipa_character, preceding_phonemes, following_phonemes, word_position, remaining_words, previous_words, following_words, sentence_position, remaining_sentences, is_quoted, is_emphasized, is_content, is_question, is_exclamation, transformed_parameters, initial_parameter_count_zero - i, preceding_parameters, following_parameters, parameters)
			f0_multiplier *= multiplier
			preceding_parameters = preceding_parameters + preceding_params
			following_parameters = following_params + following_parameters
			
		#Add everything that came out of the process to the parameters lists.
		transformed_parameters += preceding_parameters + [parameters] + following_parameters
		f0_multipliers += [f0_multiplier] * (len(preceding_parameters) + 1 + len(following_parameters))
	return (transformed_parameters, f0_multipliers)
	