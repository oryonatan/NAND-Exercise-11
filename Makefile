all:
	chmod +x JackCompiler

easy:
	python3 JackCompiler.py Seven

moderate:
	python3 JackCompiler.py ConvertToBin

hard:
	python3 JackCompiler.py Square

average:
	python3 JackCompiler.py Average

pong:
	python3 JackCompiler.py Pong

final:
	python3 JackCompiler.py ComplexArrays

testSeven:
	@rm -f sevenOutput.log
	python3 JackCompiler.py Seven > sevenOutput.log

testPong:
	@rm -f pongOutput.log
	python3 JackCompiler.py Pong > pongOutput.log

testAverage:
	@rm -f averageOutput.log
	python3 JackCompiler.py Average > averageOutput.log

testSquare:
	@rm -f squareOutput.log
	python3 JackCompiler.py Square > squareOutput.log

testComplexArrays:
	@rm -f complexArraysOutput.log
	python3 JackCompiler.py ComplexArrays > complexArraysOutput.log

testConvertToBin:
	@rm -f convertToBinOutput.log
	python3 JackCompiler.py ConvertToBin > convertToBinOutput.log

test: testSeven testPong testAverage testSquare testComplexArrays testConvertToBin easy moderate

clean:
	@rm -f sevenOutput.log
	@rm -f pongOutput.log
	@rm -f averageOutput.log
	@rm -f SquareOutput.log
	@rm -f complexArraysOutput.log
	@rm -f convertToBinOutput.log

.PHONY: clean testSeven testPong testAverage testSquare testComplexArrays testConvertToBin test tiny easy moderate hard average pong final all
