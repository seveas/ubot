.PHONY: clean doc

all: README doc

README: doc/index.rst
	awk '/^\.\./{exit} {print}' < $< > $@

doc:
	$(MAKE) -C doc html

clean:
	$(MAKE) -C doc clean
