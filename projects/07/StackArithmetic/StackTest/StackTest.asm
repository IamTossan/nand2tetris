// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1

// eq
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@JEQ.0
D;JEQ
@SP
A=M-1
M=0
@END.JEQ.0
0;JMP
(JEQ.0)
@SP
A=M-1
M=-1
(END.JEQ.0)

// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1

// eq
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@JEQ.1
D;JEQ
@SP
A=M-1
M=0
@END.JEQ.1
0;JMP
(JEQ.1)
@SP
A=M-1
M=-1
(END.JEQ.1)

// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1

// eq
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@JEQ.2
D;JEQ
@SP
A=M-1
M=0
@END.JEQ.2
0;JMP
(JEQ.2)
@SP
A=M-1
M=-1
(END.JEQ.2)

// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1

// lt
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@LT.3
D;JGE
@SP
A=M-1
M=-1
@END.LT.3
0;JMP
(LT.3)
@SP
A=M-1
M=0
(END.LT.3)

// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1

// lt
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@LT.4
D;JGE
@SP
A=M-1
M=-1
@END.LT.4
0;JMP
(LT.4)
@SP
A=M-1
M=0
(END.LT.4)

// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1

// lt
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@LT.5
D;JGE
@SP
A=M-1
M=-1
@END.LT.5
0;JMP
(LT.5)
@SP
A=M-1
M=0
(END.LT.5)

// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1

// gt
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@GLE.6
D;JLE
@SP
A=M-1
M=-1
@END.GLE.6
0;JMP
(GLE.6)
@SP
A=M-1
M=0
(END.GLE.6)

// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1

// gt
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@GLE.7
D;JLE
@SP
A=M-1
M=-1
@END.GLE.7
0;JMP
(GLE.7)
@SP
A=M-1
M=0
(END.GLE.7)

// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1

// gt
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D
D=M
@GLE.8
D;JLE
@SP
A=M-1
M=-1
@END.GLE.8
0;JMP
(GLE.8)
@SP
A=M-1
M=0
(END.GLE.8)

// push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1

// add
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M+D

// push constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1

// sub
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D

// neg
@SP
A=M-1
M=-M

// and
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=D&M

// push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1

// or
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=D|M

// not
@SP
A=M-1
M=!M

