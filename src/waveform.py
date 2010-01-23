# -*- coding: utf-8 -*-
"""
CPSC 599 module: klatt

Purpose
=======
 Provides a convenient wrapper for writing waveform data.
 
Legal
=====
 All code, unless otherwise indicated, is original, and subject to the
 terms of the GPLv3, which is provided in COPYING.
 
 (C) Neil Tallim, 2009
"""
import struct
import wave

class WaveForm(object):
	"""
	Provides an interface for dumping 16-bit signed integer data into a wavefile.
	"""
	_finalized = False #: True when this file has been closed.
	_wavefile = None #: The file into which wave data will be written.
	
	def __init__(self, filename):
		"""
		Opens a wavefile and prepares it to receive data at 10,000Hz.
		
		@type filename: basestring
		@param filename: The path to the wavefile to be written.
		
		@raise IOError: If the specified file cannot be opened for writing.
		"""
		self._wavefile = wave.open(filename, 'wb')
		self._wavefile.setnchannels(1) #Mono.
		self._wavefile.setsampwidth(2) #16-bit.
		self._wavefile.setframerate(10000) #10000 frames per second.
		
	def addSamples(self, samples):
		"""
		Adds an arbitrary number of integers to the wavefile.
		
		@type samples: sequence
		@param samples: A collection of 16-bit signed integers. (-32768-32767)
		
		@raise IOError: If the wavefile cannot be written to, either because the
		    disk is full or the wavefile has been closed.
		@raise struct.error: If a sample value is not in the acceptable integer
		    range.
		"""
		if self._finalized:
			raise IOError("The waveform has already been finalized.")
		self._wavefile.writeframes(''.join([struct.pack('h', sample) for sample in samples]))
		
	def close(self):
		"""
		Closes the wavefile, thereby finalizing its header and making it possible
		for conventional playback/analysis software to access its contents.
		
		It is safe to call this function multiple times.
		"""
		if not self._finalized:
			self._wavefile.close()
			self._finalized = True
			