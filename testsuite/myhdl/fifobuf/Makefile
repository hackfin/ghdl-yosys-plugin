test:
	python test_fifobuf.py
	cp fifobuffer.dot fifobuffer.prev.dot

%.pdf: %.dot
	dot -Tpdf $< -o $@

diff: fifobuffer.pdf fifobuffer.prev.pdf
	diffpdf $^

.PHONY: test
