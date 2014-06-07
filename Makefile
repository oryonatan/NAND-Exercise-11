easy:
	python JackCompiler.py Seven

moderate:
	python JackCompiler.py ConvertToBin

hard:
	python JackCompiler.py Square

average:
	python JackCompiler.py Average

pong:
	python JackCompiler.py Pong

final:
	python JackCompiler.py ComplexArrays

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

test: testSeven testPong testAverage testSquare testComplexArrays testConvertToBin easy moderate

clean:
	@rm -f sevenOutput.log
	@rm -f pongOutput.log
	@rm -f averageOutput.log
	@rm -f SquareOutput.log
	@rm -f complexArraysOutput.log
	@rm -f convertToBinOutput.log

.PHONY: clean testSeven testPong testAverage testSquare testComplexArrays testConvertToBin test tiny easy moderate hard average pong final
