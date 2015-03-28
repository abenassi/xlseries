# using regular expressions
import re
x = re.compile("a(b|c)d+e")
print x.match("abddde")

# using PEGs
import parsley
x = parsley.makeGrammar("foo = 'a' ('b' | 'c') 'd'+ 'e'", {})
print x("abdde").foo()

# splitting ther rules
x = parsley.makeGrammar("""
    foo = 'a' baz 'd'+ 'e'
    baz = 'b' | 'c'
    """, {})
print x("abdde").foo()

# assign match results to python variables
x = parsley.makeGrammar("""
foo = 'a':one baz:two 'd'+ 'e' -> (one, two)
baz = 'b' | 'c'
""", {})
print x("abdde").foo()

# using python expressions
x = parsley.makeGrammar("""
digit = anything?:x ?(x in '0123456789') -> x
""", {})
print x("4").digit()

# repeated matches make lists
x = parsley.makeGrammar("""
digit = anything:x ?(x in '0123456789') -> x
number = digit+
""", {})
print x("314159").number()

# collecting chunks of input
x = parsley.makeGrammar("""
digit = anything:x ?(x in '0123456789')
number = <digit+>:ds -> int(ds)
""", {})
print x("11235").number()

# building a calculator
x = parsley.makeGrammar("""
digit = anything:x ?(x in '0123456789')
number = <digit+>:ds -> int(ds)
expr = number:left ( '+' number:right -> left + right
                   | -> left)
""", {})
print x("17+34").expr()
print x("18").expr()

# adding substraction
x = parsley.makeGrammar("""
digit = anything:x ?(x in '0123456789')
number = <digit+>:ds -> int(ds)
expr = number:left ( '+' number:right -> left + right
                   | '-' number:right -> left - right
                   | -> left)
""", {})
print x("17+34").expr()
print x("18").expr()
print x("2-1").expr()

# using whitespace
x = parsley.makeGrammar("""
number = <digit+>:ds -> int(ds)
ws = ' '*
expr = number:left ws ('+' ws number:right -> left + right
                      |'-' ws number:right -> left - right
                      | -> left)
""", {})
print x("17+ 34").expr()
print x("18").expr()
print x("2 -1").expr()

# using addition and substraction at the same time
x = parsley.makeGrammar("""
number = <digit+>:ds -> int(ds)
ws = ' '*
add = '+' ws number:n -> ('+', n)
sub = '-' ws number:n -> ('-', n)
addsub = ws (add | sub)
expr = number:left (addsub+:right -> right
                   | -> left)
""", {})
print x("1 + 2 - 3").expr()


# introducing calculations passing python objects to the parser
def calculate(start, pairs):
    result = start
    for op, value in pairs:
        if op == '+':
            result += value
        elif op == '-':
            result -= value
    return result
x = parsley.makeGrammar("""
number = <digit+>:ds -> int(ds)
ws = ' '*
add = '+' ws number:n -> ('+', n)
sub = '-' ws number:n -> ('-', n)
addsub = ws (add | sub)
expr = number:left (addsub+:right -> calculate(left, right)
                   | -> left)
""", {"calculate": calculate})
print x("4 + 5 - 6").expr()


# adding multiplication and division
def calculate(start, pairs):
    result = start
    for op, value in pairs:
        if op == '+':
            result += value
        elif op == '-':
            result -= value
        elif op == '*':
            result *= value
        elif op == '/':
            result /= value
    return result
x = parsley.makeGrammar("""
number = <digit+>:ds -> int(ds)
ws = ' '*
add = '+' ws expr2:n -> ('+', n)
sub = '-' ws expr2:n -> ('-', n)
mul = '*' ws number:n -> ('*', n)
div = '/' ws number:n -> ('/', n)

addsub = ws (add | sub)
muldiv = ws (mul | div)

expr = expr2:left addsub*:right -> calculate(left, right)
expr2 = number:left muldiv*:right -> calculate(left, right)
""", {"calculate": calculate})
print x("4 * 5 + 6").expr()


# adding parenthesis
def calculate(start, pairs):
    result = start
    for op, value in pairs:
        if op == '+':
            result += value
        elif op == '-':
            result -= value
        elif op == '*':
            result *= value
        elif op == '/':
            result /= value
    return result
x = parsley.makeGrammar("""
number = <digit+>:ds -> int(ds)
parens = '(' ws expr:e ws ')' -> e
value = number | parens
ws = ' '*
add = '+' ws expr2:n -> ('+', n)
sub = '-' ws expr2:n -> ('-', n)
mul = '*' ws value:n -> ('*', n)
div = '/' ws value:n -> ('/', n)

addsub = ws (add | sub)
muldiv = ws (mul | div)

expr = expr2:left addsub*:right -> calculate(left, right)
expr2 = value:left muldiv*:right -> calculate(left, right)
""", {"calculate": calculate})

print x("4 * (5 + 6) + 1").expr()
