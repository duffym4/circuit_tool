from util import sign
import sympy

class Measure():

    unitPrefixes = {
        "μ": -6,
        "m": -3,
        "": 0,
        "k": 3,
        "M": 6
    }

    def __init__(self, value, unit, prefix = ""):
        self.value = value
        self.unit = unit
        self.unitPrefix = prefix

    def isNumber(self):
        try:
            test = ('%.4f' % self.float()).rstrip('0').rstrip('.')
            return True
        except:
            return False

    # Converts fraction str to float. Ignores unitPrefix
    def float(self):
        try:
            return float(str(self.value))
        except ValueError:
            try:
                num, denom = str(self.value).split('/')
            except ValueError:
                return None
            try:
                leading, num = num.split(' ')
            except ValueError:
                return float(num) / float(denom)
            if float(leading) < 0:
                sign_mult = -1
            else:
                sign_mult = 1
            return float(leading) + sign_mult * (float(num) / float(denom))

    # Returns the numerical representation of value * 10**unitPrefix
    def number(self):
        return self.float() * 10**self.unitPrefixes[self.unitPrefix]

    # Strips zeroes from float for better printing
    def prettyFloat(self):
        if self.isNumber():
            return ('%.4f' % self.float()).rstrip('0').rstrip('.')
        return sympy.pretty(self.value) + " "

    # Formats value for lcapy in format [value]e[unitPrefix]
    def lcapyStr(self):
         if not self.isNumber():
             return "{" + "".join(self.value.split()) + "}"
         return self.prettyFloat() + "e" + str(self.unitPrefixes[self.unitPrefix])

    # Returns a string with a pretty float and the unit
    def str(self):
        return self.prettyFloat() + self.unitPrefix + self.unit

    # Chooses a prefix that optimizes readability
    def autoPrefix(self):
        if not self.isNumber():
            return ""
        num = abs(self.number())
        if num == 0:
            self.value, self.unitPrefix = 0, ""
            return
        for prefix in self.unitPrefixes:
            power = self.unitPrefixes[prefix]
            if power < 0 and num < 10**(power+3) or power > 0 and num >= 10**power:
                self.value = sign(self.float()) * (num/(10**power))
                self.unitPrefix = prefix
                if power < 0:
                    return
