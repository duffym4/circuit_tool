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

    def float(self):
        try:
            return float(self.value)
        except ValueError:
            try:
                num, denom = self.value.split('/')
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

    def prettyFloat(self):
        return ('%f' % self.float()).rstrip('0').rstrip('.')

    def lcapyStr(self):
         return self.prettyFloat() + "e" + str(self.unitPrefixes[self.unitPrefix])

    def str(self):
        return self.prettyFloat() + self.unitPrefix + self.unit
