// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(IDLELOOP)

@KBD
D=M
@IDLELOOP
D;JEQ

// paint screen
@i
M=0
(PAINTLOOP)
@i
D=M
@8191
D=D-A
@PRESSEDLOOP
D;JGT

@SCREEN
D=A
@i
A=D+M
M=-1

@i
M=M+1
@PAINTLOOP
0;JMP

(PRESSEDLOOP)

@KBD
D=M
@PRESSEDLOOP
D;JNE

// clear screen
@i
M=0

(CLEARLOOP)
@i
D=M
@8191
D=D-A
@IDLELOOP
D;JGT

@SCREEN
D=A
@i
A=D+M
M=0

@i
M=M+1
@CLEARLOOP
0;JMP
