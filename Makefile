tiny:
	python JackCompiler.py Seven

testSeven:
	@rm -f sevenOutput.log
	python JackCompiler.py Seven > sevenOutput.log

testPong:
	@rm -f pongOutput.log
	python JackCompiler.py Pong > pongOutput.log

testAverage:
	@rm -f averageOutput.log
	python JackCompiler.py Average > averageOutput.log

testSquare:
	@rm -f squareOutput.log
	python JackCompiler.py Square > squareOutput.log

testComplexArrays:
	@rm -f complexArraysOutput.log
	python JackCompiler.py ComplexArrays > complexArraysOutput.log

testConvertToBin:
	@rm -f convertToBinOutput.log
	python JackCompiler.py ConvertToBin > convertToBinOutput.log

tokens:
	python JackCompiler.py Pong > pongNaive.xml

test: testSeven testPong testAverage testSquare testComplexArrays testConvertToBin tokens

clean:
	@rm -f sevenOutput.log
	@rm -f pongOutput.log
	@rm -f averageOutput.log
	@rm -f SquareOutput.log
	@rm -f complexArraysOutput.log
	@rm -f convertToBinOutput.log

.PHONY: clean testSeven testPong testAverage testSquare testComplexArrays testConvertToBin test tiny