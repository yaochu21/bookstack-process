class A:
    def __init__(self,a=0) -> None:
        self.a = a
    
    def __str__(self) -> str:
        return "a: "+str(self.a)

class B(A):
    def __init__(self) -> None:
        super().__init__(2)
        self.b = 1

    def __str__(self) -> str:
        return super().__str__() + "; b: 1"

lst = [A(),A(),B()]

print([str(l) for l in lst])

for i,l in enumerate(lst):
    lst[i] = A(l.a)

print([str(l) for l in lst])