AUTOMAKE_OPTIONS = foreign
SUBDIRS = bin lib helpers plib rlib doc data

README: doc/index.rst
	@AWK@ '/^Table of contents/{exit} {print}' < $< > $@
