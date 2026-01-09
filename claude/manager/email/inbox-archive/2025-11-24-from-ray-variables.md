From: Ray

Please add a new project to examine what would be needed to support Javascript variables in the transpiler.
We might allow local variables of the form:
let foo = 1;

And global variables with:
var bar = 3;

Local variables would probably be handled by substituting the expression. So this code:
```
let foo = 5;
gvar[1] = foo;
```

becomes:
```
gvar[1] = 5;
```

Global variables declared with "var" might become aliases for gvars, starting with gvar[7] and working down, making use of gvars that are not explicitly used by the user code. So this Javascript:
```
var foo = 5;
gvar[1] = foo;
```

Would be equilavent to:
```
gvar[7]  = 5;
gvar[1] = gvar[7];
```

Other approaches could also be considered.

Likely, the decompiler would not be able to recover these variables.
