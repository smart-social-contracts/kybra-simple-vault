import ggg
from pprint import pprint

ggg.base.initialize()

# pprint(ggg.base.universe())
# pprint(ggg.World['Earth'].to_dict())
# land = ggg.Land.new(open(r'/home/user/dev/the_project/app/tests/fixtures/switzerland.geojson').read(), ggg.World['Earth'])
# pprint(land.to_dict())


# Create a LAND token
land_token = ggg.Token.new(symbol="LAND", name="Land Ownership Token")

# Mint tokens for a user
land_token.mint(
    "owner1",
    1000,  # 1000 units of land
    metadata={"location": "Plot 42, Springfield", "land_type": "Agricultural"}
)

# Check balances and metadata
print(land_token.balance("owner1"))  # Output: 1000 (1 token = 1 unit of land)
print(land_token.get_metadata("owner1"))
# Output: [{'location': 'Plot 42, Springfield', 'land_type': 'Agricultural', 'surface_area': 1000}]


# Transfer 500 tokens (500 units of land) to another address
land_token.transfer(from_address="owner1", to_address="owner2", amount=500)

# Check balances and metadata
print(land_token.balance("owner1"))  # Output: 500
print(land_token.balance("owner2"))  # Output: 500

print(land_token.get_metadata("owner1"))
# Output: Metadata for the remaining 500 units of land
print(land_token.get_metadata("owner2"))
# Output: Metadata for the transferred 500 units of land

land_token.save()

pprint(ggg.base.universe())
