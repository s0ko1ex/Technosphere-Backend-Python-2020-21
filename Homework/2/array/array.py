from itertools import zip_longest


class MyArray(list):
    def __lt__(self, other):
        return sum(self) < sum(other)

    def __le__(self, other):
        return sum(self) <= sum(other)

    def __gt__(self, other):
        return sum(self) > sum(other)

    def __ge__(self, other):
        return sum(self) >= sum(other)

    def __eq__(self, other):
        return sum(self) == sum(other)

    def __ne__(self, other):
        return sum(self) != sum(other)

    def __add__(self, other):
        return MyArray([a[0] + a[1]
                        for a in zip_longest(self, other, fillvalue=0)])

    def __radd__(self, other):
        return MyArray([a[0] + a[1]
                        for a in zip_longest(self, other, fillvalue=0)])

    def __sub__(self, other):
        return MyArray([a[0] - a[1]
                        for a in zip_longest(self, other, fillvalue=0)])

    def __rsub__(self, other):
        return MyArray([a[1] - a[0]
                        for a in zip_longest(self, other, fillvalue=0)])
