// function SimpleFunction.test 2
(SimpleFunction.test)
@SP
A=M
M=0
@SP
M=M+1
@SP
A=M
M=0
@SP
M=M+1

// push local 0
@0
D=A
@LCL
D=M+D
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

// push local 1
@1
D=A
@LCL
D=M+D
A=D
D=M
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

// not
@SP
A=M-1
M=!M

// push argument 0
@0
D=A
@ARG
D=M+D
A=D
D=M
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

// push argument 1
@1
D=A
@ARG
D=M+D
A=D
D=M
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

// return
@SP
A=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D
@R13
D=M-1
A=D
D=M
@THAT
M=D
@13
M=M-1
@R13
D=M-1
A=D
D=M
@THIS
M=D
@13
M=M-1
@R13
D=M-1
A=D
D=M
@ARG
M=D
@13
M=M-1
@R13
D=M-1
A=D
D=M
@LCL
M=D
@R14
A=M
0;JMP

