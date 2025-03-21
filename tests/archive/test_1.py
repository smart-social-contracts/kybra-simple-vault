import ggg
from pprint import pprint

ggg.base.initialize()
pprint(ggg.base.universe())

ext = ggg.ExtensionCode['DEFAULT_EXTENSION_CODE_ORGANIZATION']
print(ext.to_dict())

org0 = ggg.Organization.new()
pprint(org0.to_dict())

org1 = ggg.Organization.new('org1')
pprint(org1.to_dict())


print(50 * '*')
pprint(ggg.base.universe())
