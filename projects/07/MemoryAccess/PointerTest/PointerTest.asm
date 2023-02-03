// push constant 3030
@3030
D=A
// RAM[SP] = D
@SP
A=M
M=D
// SP++
@SP
M=M+1

// pop pointer 0
@SP
M=M-1
@SP
A=M
D=M
@THIS
M=D

// push constant 3040
@3040
D=A
// RAM[SP] = D
@SP
A=M
M=D
// SP++
@SP
M=M+1

// pop pointer 1
@SP
M=M-1
@SP
A=M
D=M
@THAT
M=D

// push constant 32
@32
D=A
// RAM[SP] = D
@SP
A=M
M=D
// SP++
@SP
M=M+1

// pop this 2
@SP
M=M-1
@2
D=A
@THIS
D=M+D
@R13
M=D
@SP
A=M
D=M
@R13
A=M
M=D

// push constant 46
@46
D=A
// RAM[SP] = D
@SP
A=M
M=D
// SP++
@SP
M=M+1

// pop that 6
@SP
M=M-1
@6
D=A
@THAT
D=M+D
@R13
M=D
@SP
A=M
D=M
@R13
A=M
M=D

// push pointer 0
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1

// push pointer 1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1

// add
// SP--
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M+D

// push this 2
@2
D=A
@THIS
D=M+D
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

// sub
// SP--
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D

// push that 6
@6
D=A
@THAT
D=M+D
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

// add
// SP--
@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M+D

