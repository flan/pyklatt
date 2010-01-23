# -*- coding: utf-8 -*-
"""
CPSC 599 module: src.parwave

Purpose
=======
 Provides functionality for generating waveform samples from format parameter
 data.
 
Legal
=====
 All code, unless otherwise indicated, is original, and subject to the
 terms of the GPLv3, which is provided in COPYING.
 
 This project borrows algorithms, ideas, and statistical data from other
 projects. Full attribution is provided in ACKNOWLEDGEMENTS.
 
 (C) Neil Tallim, Sydni Bennie, 2009
"""
import math
import random

FREQUENCY = 10 #: A number that indicates the frequency of synthesized speech, as a multiple of 1000Hz.
_F0_HZ = 80 #: The core rate at which sounds will repeat, controlling pitch.

class Synthesizer(object):
	"""
	Enables synthesis of sounds based on parameter values, as described in the
	referenced papers.
	"""
	_cascade_resonators = None #: A collection of resonators to handle formants 1-6 in a cascading fashion.
	_glottal_antiresonator = None #: An anti-resonator for glottal frequencies.
	_glottal_pole_resonator = None #: A resonator for glottal pole frequencies.
	_glottal_sine_resonator = None #: A resonator for glottal sine frequencies.
	_nasal_antiresonator = None #: An anti-resonator for nasal frequencies.
	_nasal_pole_resonator = None #: A resonator for nasal pole frequencies.
	_noise = 0.0 #: The last-generated random noise value, needed for echoing.
	_parallel_resonators = None #: A collection of resonators to handle formants 2-6 in parallel.
	
	def __init__(self):
		"""
		Prepares all resonator objects needed by this synthesizer.
		"""
		self._cascade_resonators = (
		 _Resonator(),
		 _Resonator(),
		 _Resonator(),
		 _Resonator(),
		 _Resonator(),
		 _Resonator()
		)
		self._parallel_resonators = (
		 _Resonator(),
		 _Resonator(),
		 _Resonator(),
		 _Resonator(),
		 _Resonator(),
		)
		self._glottal_antiresonator = _AntiResonator()
		self._glottal_pole_resonator = _Resonator()
		self._glottal_sine_resonator = _Resonator()
		self._nasal_antiresonator = _AntiResonator()
		self._nasal_pole_resonator = _Resonator()
		
	def generateSilence(self, milliseconds):
		"""
		Generates a period of silence and resets the noise value.
		
		@type milliseconds: int
		@param milliseconds: The number of milliseconds of silence to be
		    generated.
		
		@rtype: tuple
		@return: A collection of 0s, equal in length to milliseconds * 10.
		"""
		self._noise = 0.0
		return (0,) * int(milliseconds * FREQUENCY)
		
	def synthesize(self, parameters, f0_multiplier, turbo):
		"""
		Renders the given parameters in a sinewave pattern, with period being
		defined based on the given formant frequencies and an f0 pulse, and
		amplitude being a function of bandwidth, base amplitude values, white
		noise, and resonance.
		
		@type parameters: sequence(33)
		@param parameters: A collection of synthesis parameters, as described in
		    L{ipa.IPA_PARAMETERS} and L{ipa.IPA_DATA}.
		@type f0_multiplier: number
		@param f0_multiplier: A modifier to apply to the f0 period. Larger vowels
		    mean slower pitch.
		@type turbo: bool
		@param turbo: If set, repeats a single period's synthesized values for the
		    entire duration of the sound, sacrificing subtle quality for speed.
		
		@rtype: tuple
		@return: A collection of integers between -32768 and 32767 that represent
		    synthetic speech.
		"""
		#Initialize parameters required for synthesis.
		f0_hz = int(_F0_HZ * f0_multiplier)
		(fgp, fgz, fgs, fnp, fnz,
		 f1, f2, f3, f4, f5, f6,
		 bgp, bgz, bgs, bnp, bnz,
		 bw1, bw2, bw3, bw4, bw5, bw6,
		 a2, a3, a4, a5, a6,
		 ab, ah, af, av, avs,
		 milliseconds) = parameters
		
		#Prepare all resonators.
		self._initResonators(
		 (fgp, fgz, fgs, fnp, fnz, f1, f2, f3, f4, f5, f6),
		 (bgp, bgz, bgs, bnp, bnz, bw1, bw2, bw3, bw4, bw5, bw6)
		)
		
		#Multiplex resonator collections.
		resonator_collection = tuple([(c_r, p_r, a) for (c_r, p_r, a) in reversed(zip(self._cascade_resonators[1:], self._parallel_resonators, (a2, a3, a4, a5, a6)))])
		cascade_resonator_1 = self._cascade_resonators[0]
		
		#Set loop variables.
		sounds = []
		last_result = 0
		period_index = f0_hz
		samples_target = int(milliseconds * FREQUENCY)
		for t in xrange(samples_target + f0_hz): #Run for the specified number of milliseconds, plus one full period to discard initial clicks.
			noise = self._getNoise()
			
			#Apply linear f0 approximation.
			pulse = 0.0
			if period_index == f0_hz:
				pulse = 1.0
				period_index = 0
			else:
				period_index += 1
				
			#Compute cascade value.
			source = self._glottal_pole_resonator.resonate(pulse)
			source = (self._glottal_antiresonator.resonate(source) * av) + (self._glottal_sine_resonator.resonate(source) * avs)
			source += noise * ah
			source = self._nasal_pole_resonator.resonate(source)
			source = self._nasal_antiresonator.resonate(source)
			
			frication = noise * af
			
			result = frication * ab #Seed parallel value.
			for (cascade_resonator, parallel_resonator, amplitude) in resonator_collection:
				source = cascade_resonator.resonate(source) #Update cascade value.
				result += parallel_resonator.resonate(frication * amplitude) #Update parallel value.
			result += cascade_resonator_1.resonate(source) #: Add final cascade value to final parallel value.
			
			output = result - last_result #Subtract last result from new result to introduce a micro-period into the waveform so it's audible to humans.
			last_result = result
			if t >= f0_hz: #Skip the first period to avoid popping.
				output = int(output * 32767.0) #Convert the result to an integer on an appropriate scale.
				#Constrain the output range, by clipping if necessary.
				if output > 32767:
					output = 32767
				elif output < -32768:
					output = -32768
				sounds.append(output)
				
				#Apply turbo mode processing.
				if turbo and t == f0_hz * 2 - 1:
					while len(sounds) * 2 < samples_target:
						sounds *= 2
					sounds += sounds[:samples_target - len(sounds)]
					break
		return tuple(sounds)
		
	def _initResonators(self, frequencies, bandwidths):
		"""
		Initializes all resonators needed for rendering sound from parameter
		values.
		
		@type frequencies: sequence(11)
		@param frequencies: (fgp, fgz, fgs, fnp, fnz, f1, f2, f3, f4, f5, f6)
		    from the input parameters.
		@type bandwidths: sequence(11)
		@param bandwidths: (bgp, bgz, bgs, bnp, bnz, bw1, bw2, bw3, bw4, bw5, bw6)
		    from the input parameters.
		"""
		#I don't know the significance of this math, unfortunately.
		pi_neg_div = math.pi * -0.0001
		pi_2_div = 2.0 * math.pi * 0.0001
		pi_neg_2_div = -pi_2_div
		
		b = (bgp, bgz, bgs, bnp, bnz, b1, b2, b3, b4, b5, b6) = [n * m for (n, m) in zip([math.cos(pi_2_div * f) for f in frequencies], [2 * math.e ** (pi_neg_div * bw) for bw in bandwidths])]
		c = (cgp, cgz, cgs, cnp, cnz, c1, c2, c3, c4, c5, c6) = [-math.e ** (pi_neg_2_div * bw) for bw in bandwidths]
		a = (agp, agz, ags, anp, anz, a1, a2, a3, a4, a5, a6) = [1 - b_v - c_v for (b_v, c_v) in zip(b, c)]
		
		self._cascade_resonators[0].init(a1, b1, c1)
		for (a_n, b_n, c_n, c_r, p_r) in zip(a[6:], b[6:], c[6:], self._cascade_resonators[1:], self._parallel_resonators):
			p_r.init(a_n, b_n, c_n)
			c_r.init(a_n, b_n, c_n)
		self._glottal_pole_resonator.init(agp, bgp, cgp)
		self._glottal_sine_resonator.init(ags, bgs, cgs)
		self._nasal_pole_resonator.init(anp, bnp, cnp)
		self._glottal_antiresonator.init(agz, bgz, cgz)
		self._nasal_antiresonator.init(anz, bnz, cnz)
		
	def _getNoise(self):
		"""
		Generates a random number and adds it to the last-generated random value.
		
		@rtype: float
		@return: A random value, half of which is echoed.
		"""
		self._noise = random.uniform(-0.00001, 0.00001) + self._noise
		return self._noise
		
		
class _Resonator(object):
	"""
	A simulator of a two-tier echoing chamber.
	"""
	_a = None #: The co-efficient for the input value in each cycle.
	_b = None #: The co-efficient for the value stored in the last cycle.
	_c = None #: The co-efficient for the value stored in the second-last cycle.
	_delay_1 = None #: The last-stored value for use in successive resonance.
	_delay_2 = None #: The second-last-stored value for use in successive resonance.
	
	def init(self, a, b, c):
		"""
		Sets the resonance paramters and resets the echo queue.
		
		@type a: number
		@param a: The value to be multiplied by the input.
		@type b: number
		@param b: The value to be multiplied by the last-generated output.
		@type c: number
		@param c: The value to be multiplied by the second-last-generated output.
		"""
		self._a = a
		self._b = b
		self._c = c
		self._delay_1 = self._delay_2 = 0.0
		
	def resonate(self, input):
		"""
		Resonates the input value, producing output.
		
		The output value is stored for use in successive resonance.
		
		@type input: number
		@param input: The value to be resonated.
		
		@rtype: float
		@return: The result of resonance.
		"""
		output = self._resonate(input)
		self._delay_1 = output
		return output
		
	def _resonate(self, input):
		"""
		Employs two-tier echoing to resonate the input value as though it were
		passing through a chamber.
		
		@type input: number
		@param input: The value to be resonated.
		
		@rtype: float
		@return: The result of resonance.
		"""
		output = self._a * input + self._b * self._delay_1 + self._c * self._delay_2
		self._delay_2 = self._delay_1
		return output
		
class _AntiResonator(_Resonator):
	"""
	A variant on the resonator that generates inverse harmonics.
	"""
	def init(self, a, b, c):
		"""
		Sets the resonance paramters and resets the echo queue.
		
		@type a: number
		@param a: The reciprocal of the value to be multiplied by the input.
		@type b: number
		@param b: The value to be multiplied by -1.0/a and the last-stored input.
		@type c: number
		@param c: The value to be multiplied by -1.0/a and the second-last-stored
		    input.
		"""
		a = 1.0 / a
		_Resonator.init(self, a, -b * a, -c * a)
		
	def resonate(self, input):
		"""
		Resonates the input value, producing output.
		
		The input value is stored for use in successive resonance.
		
		@type input: number
		@param input: The value to be resonated.
		
		@rtype: float
		@return: The result of resonance.
		"""
		output = self._resonate(input)
		self._delay_1 = input
		return output
		