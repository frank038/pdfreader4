# pdfreader4
pdf reader - early version

Requirements:
- python3
- gtk4 bindings
- poppler bindings
- python3-cairo (optional for the custom image annotation)

Usage: python3 pdfreader4 FILE.pdf

Features:
- tabs
- open and save and print
- table of contents
- navigation
- opens pdf files with password
- text selection: ctrl+left mouse button
- searching (partial implementation; can search only whole words)
- annotations: text, square, circle, free text, stamp (with custom image of type png); except for the text annotation (just click in the page whatever you want), the other ones works this way: after having chosen the type of the annotation, press the left mouse button in the page (the starting point) and drag; release the mouse button
- annotations: can be added (from toolbar) or removed (right mouse button on it); the colour of the annotation icon to be added can be changed, also the borderd width can be changed, if supported by the annotation
- annotations: the esc key cancel the choise
- annotations, custom image: the png image aspect ratio is preserved, so the final size of the image in the page depends on the with of the selection
- configuration file config.json: toolbar icon size, paper colour, text selection colour background and foreground; fixed window size.

