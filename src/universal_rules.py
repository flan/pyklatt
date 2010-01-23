# -*- coding: utf-8 -*-
"""
CPSC 599 module: src.universal_rules

Purpose
=======
 Contains a collection of rules to apply to phonemes, regardless of language.
 
Legal
=====
 All code, unless otherwise indicated, is original, and subject to the
 terms of the GPLv3, which is provided in COPYING.
 
 (C) Neil Tallim, Sydni Bennie, 2009
"""
import ipa

def bridgeWords(ipa_character, preceding_phonemes, following_phonemes, previous_words, parameters_list):
	"""
	Inserts a pause between two vowels in co-located words, or causes the second
	word's initial vowel, if present, to adopt the sound of the previous word's
	terminal consonant.
	
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
	@type previous_words: sequence
	@param previous_words: A collection of all words that have been previously
	    synthesized.
	@type parameters_list: list
	@param parameters_list: A collection of all sounds currently associated with
	    the IPA character being processed.
	
	@rtype: list
	@return: An updated list of parameters.
	
	@author: Sydni Bennie
	"""
	parameters_list = parameters_list[:]
	
	if not ipa_character in ipa.VOWELS:
		return parameters_list
		
	if not preceding_phonemes and previous_words:
		character = previous_words[-1][-1]
		if character in ipa.VOWELS:
			parameters_list.append(list(ipa.IPA_PARAMETERS[u'h'][:32]) + [50])
		else:
			values = zip(parameters_list[0][:32], ipa.IPA_PARAMETERS[character[:32]])
			parameters_list.insert(0, [(c + v) / 2 for (v, c) in values] + [50])
	return parameters_list
	
def nasalizeVowel(ipa_character, following_phonemes, parameters_list):
	"""
	Lops off half of the current sound, if it's a vowel followed by a nasal, and
	inserts one sixth and one third of its duration as two nasalized variants of
	the vowel's parameters.
	
	The input list of parameters is not altered by this function.
	
	Nasalization concept inspired by a function described in "Klatt Synthesizer
	in Simulink®", a graduate research paper written by Sean McLennan in 2000 for
	S522 - Digital Signal Processing under Dr. Diane Kewley-Port at Indiana
	University. This information, lacking in-text licensing terms, is presumed to
	have been published as public-domain work or otherwise under terms agreeable
	to non-commercial academic research.
	
	The referenced paper was retrieved from
	http://www.shaav.com/professional/linguistics/klatt.pdf on June 7th, 2009.
	
	@type ipa_character: unicode
	@param ipa_character: The character, representative of a phoneme, being
	    processed.
	@type following_phonemes: sequence
	@param following_phonemes: A collection of all phonemes, in order, that
	    follow the current IPA character in the current word.
	@type parameters_list: list
	@param parameters_list: A collection of all sounds currently associated with
	    the IPA character being processed. The first element is assumed to be the
	    base sound, and any additional sounds will be inserted immediately after
	    it, occupying indecies 1 and 2 and offsetting any other elements in the
	    list.
	
	@rtype: list
	@return: An updated list of parameters.list(ipa.IPA_PARAMETERS[u'h'][:32]) + [15]
	
	@author: Neil Tallim
	"""
	parameters_list = parameters_list[:] #Make a local copy.
	
	if not following_phonemes or not following_phonemes[0] in ipa.NASALS:
		return parameters_list
	if not ipa_character in ipa.VOWELS or ipa_character in ipa.NASALS:
		return parameters_list
		
	#Extract vowel parameters.
	vowel = parameters_list[0]
	vowel_duration = vowel[32]
	vowel_values = vowel[:32]
	
	#Multiplex the nasal and vowel values.
	values = zip(vowel_values, ipa.IPA_PARAMETERS[following_phonemes[0]][:32])
	
	#Reduce vowel duration by 50%.
	parameters_list[0] = vowel_values + [int(vowel_duration * 0.5)]
	#Add nazalized lead-in = 1/3 nasalized sound, 2/3 base vowel.
	parameters_list.insert(1, [(v * 2 + n) / 3 for (v, n) in values] + [int(vowel_duration * 0.167)])
	#Add nasalized terminator = 2/3 nasalized sound, 1/3 base vowel.
	parameters_list.insert(2, [(v + n * 2) / 3 for (v, n) in values] + [int(vowel_duration * 0.333)])
	
	return parameters_list
	
def shapeContours(ipa_character, preceding_phonemes, following_phonemes, parameters_list):
	"""
	Lops off 15ms from the start and end of the current phoneme and blends it
	with the sounds on its edges.
	
	A glottal pause (hʔ) is inserted before stops instead of blending the sounds.
	
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
	@type parameters_list: list
	@param parameters_list: A collection of all sounds currently associated with
	    the IPA character being processed.
	
	@rtype: list
	@return: An updated list of parameters.
	
	@author: Neil Tallim
	"""
	parameters_list = parameters_list[:] #Make a local copy.
	
	if preceding_phonemes:
		lead_in_sound = parameters_list[0]
		lead_in_values = lead_in_sound[:32]
		
		#Reduce initial sound duration by 10ms.
		parameters_list[0] = lead_in_values + [max(5, lead_in_sound[32] - 15)]
		
		#Place the new sound at the start of the list.
		if not ipa_character in ipa.STOPS: #Blend the sounds, 2/3 current.
			parameters_list.insert(0, [(c * 2 + p) / 3 for (c, p) in zip(lead_in_values, ipa.IPA_PARAMETERS[preceding_phonemes[-1]][:32])] + [15])
		else: #Add a 'ʔ' gap.
			parameters_list.insert(0, list(ipa.IPA_PARAMETERS[u'\u0294'][:32]) + [15])
			
	if following_phonemes and not (ipa_character in ipa.VOWELS and following_phonemes[0] in ipa.NASALS): #Avoid nasalizing previously nasalized vowels.
		lead_out_sound = parameters_list[-1]
		lead_out_values = lead_out_sound[:32]
		
		#Reduce terminal sound duration by 10ms.
		parameters_list[-1] = lead_out_values + [max(5, lead_out_sound[32] - 15)]
		
		#Place the new sound at the end of the list.
		if not following_phonemes[0] in ipa.STOPS: #Blend the sounds, 2/3 current.
			parameters_list.append([(c * 2 + p) / 3 for (c, p) in zip(lead_out_values, ipa.IPA_PARAMETERS[following_phonemes[0]][:32])] + [15])
		else: #Add a 'h' gap.
			parameters_list.append(list(ipa.IPA_PARAMETERS[u'h'][:32]) + [15])
			
	return parameters_list
	