`PyKlatt` is a [Python](http://www.python.org) 2.x implementation of the [Klatt synthesizer model](http://scholar.google.ca/scholar?hl=en&lr=&cluster=16954812257640986259&um=1&ie=UTF-8&ei=W0lbS-SVFI-4swPploCPAw&sa=X&oi=science_links&resnum=1&ct=sl-allversions&ved=0CAsQ0AIwAA), featuring linguist-friendly IPA-based input and computer-scientist-friendly extensibility and coding. It was created as a term project for a Computational Linguistics class taught by [Sean McLennan](http://www.shaav.com/) in 2009.


---

# Overview #
The primary goal of this project was to see how well a collection of programmatically simple rules could be combined to approximate the prosody patterns of human speech, as found in Canadian English. However, a secondary goal was to create an extensible synthesizer platform on which other languages could be implemented and refinements to universal production rules and IPA-sound mappings could be shared.

This project was published to share information with other students, possibly including you, who may wish to use this work as a basis for their own exploration into the field of computational linguistics, with an open invitation to contribute what you discover to this central resource to benefit those who may stumble upon it afterwards.

## Maturity and scope ##
This project's scope is highly flexible, although it is constrained to synthesis -- any semantic processing should happen at a higher level, and it should generate synthesizable output by inserting stress markings where appropriate.

As for this project's maturity, it is actually, with a little bit of massaging, capable of producing rather comprehensible speech. For example, this is what it sounds like when producing "Hello, World!":
  * [hɛl>o, wʌ>><-ɹld!](http://pyklatt.googlecode.com/files/hello%2C_world-v1.ogg)
Note how the string of characters is plain, easy-to-read IPA with a bit of simple stress markup: the 'l' is lengthened, a comma adds a brief pause between words, the 'ʌ' is lengthened a bit more and given a lower pitch, and the statement is an exclamation. That's all that's needed as input. Seriously. No XML or scary numbers anywhere.


---

# Project information #
## Freedom of use ##
You are not required to share the source code with others, unless you distribute binaries (so you'll need to include it if you're submitting a project to a teacher, but it's Python, which means you'd have to do that anyway), so feel free to hack away to find out how it works. And, if, after you've done something cool, you want to share it with the rest of the world, submit your patch to a maintainer and it'll be committed to the repository. Alternatively, if you're planning to base a project on this code, just request commit access to the Subversion repository and it'll be granted -- just promise not to break things, 'cause working things are good.

## Usage and exploration ##
Although everything you should need to know to get this system working is explained in the README file, and the code is extensively documented, it may be helpful to have access to a browser-friendly API. So, with that said, here's the rendered epydoc for the project, as of June 25, 2009:
  * [Online API](http://static.uguu.ca/projects/ar-sphaela/PyKlatt/epydoc/) ([download](http://pyklatt.googlecode.com/files/api-june-25-2009.zip))

## Getting help ##
If you're stuck or curious about how something works, don't hesitate to ask for help. You should get a response fairly quickly.


---

# Feedback #
If you like `PyKlatt`, let us know. If you really need a specific feature, tell us. We want to help you learn so you can help us learn.


---

# Credits #
[Neil Tallim](http://uguu.ca/)
  * Programming, syntax
Sydni Bennie
  * Phonology, accessibility


---

# Contacts #
red {dot} hamsterx {at} gmail