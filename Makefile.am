AUTOMAKE_OPTIONS = foreign
SUBDIRS = bin lib helpers plib rlib doc

README: doc/index.rst
	@AWK@ '/^\.\./{exit} {print}' < $< > $@
