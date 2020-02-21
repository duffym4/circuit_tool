from qt import *

class NameValidator(QValidator):

   def __init__(self, schematic, component):
    super().__init__()
    self.schematic = schematic
    self.component = component
    self.prefix = self.component.namePrefix

   def validate(self, str, pos):
    prefix, rest = str[:1], str[1:]
    if prefix != self.prefix:
         return (QValidator.Invalid, str, pos)
    return (QValidator.Acceptable, str, pos)

   def fixup(self, str):
    if self.schematic.usedName(str, self.component):
         return self.schematic.getNextName(self.prefix)
    else:
         return str

