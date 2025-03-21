from ggg import World, State, Citizen, Organization, User


world = World("Wizarding World")

phoenix_citizen_names = """
Harry Potter
Hermione Granger
Ron Weasley
Albus Dumbledore
Sirius Black
Rubeus Hagrid
Minerva McGonagall
Neville Longbottom
Luna Lovegood
Remus Lupin
Fred Weasley
George Weasley
Ginny Weasley
Molly Weasley
Arthur Weasley
Nymphadora Tonks
Dobby
Kingsley Shacklebolt
Cedric Diggory
Aberforth Dumbledore
""".strip().split(
    "\n"
)


dark_citizen_names = """
Lord Voldemort
Tom Riddle
Bellatrix Lestrange
Lucius Malfoy
Draco Malfoy
Peter Pettigrew
Fenrir Greyback
Barty Crouch Jr.
Dolores Umbridge
Severus Snape
Narcissa Malfoy
Crabbe
Goyle
Pansy Parkinson
Amycus
Alecto
Walden Macnair
Antonin Dolohov
Thorfinn Rowle
""".strip().split(
    "\n"
)

everyone = phoenix_citizen_names + dark_citizen_names

hogwarts = State("Hogwarts", "Hogwarts School of Witchcraft and Wizardry")
dark_order = State("Dark Order", "Voldemort's Dark Order & Death Eaters")
order_phoenix = State("Order of the Phoenix")
order_dark = State("Dark Order")


for state, citizen_names in {
    order_phoenix: phoenix_citizen_names,
    order_dark: dark_citizen_names,
}:
    for name in citizen_names:
        user_name = name.replace(" ", "_").lower()
        user = User(user_name)
        user.commit()
        citizen = Citizen(name)
        citizen.commit()
        user.add_citizenship(citizen)


hogwarts.set_board(
    {
        "Lucius Malfoy": 15,
        "Arabella Greengrass": 10,
        "Horatio Burke": 12,
        "Ignatius Prewett": 8,
        "Cassandra Selwyn": 12,
        "Barnabas Cuffe": 5,
        "Marion Edgecombe": 8,
        "Octavia Fawley": 8,
        "Edgar Bones": 7,
        "Tiberius Ogden": 5,
        "Melinda Marchbanks": 10,
    }
)

dark_order.set_board(
    {
        "Lord Voldemort": 100,
    }
)


hogwarts_direction = Organization(
    "Hogwarts School direction",
    {
        "Albus Dumbledore": 70,
        "Minerva McGonagall": 30,
    },
)
hogwarts.add_subordinate(hogwarts_direction)

for department_name, responsible_names in {
    "Potions": {"Severus Snape": 100},
    "Keys, Grounds and Maginal Creatures": {"Rubeus Hagrid": 100},
    "Charms": {"Filius Flitwick": 100},
    "Herbology": {"Pomona Sprout": 100},
    "Divination": {"Sybill Trelawney": 100},
    "Defense Against the Dark Arts": {"Remus Lupin": 100},
}:
    hogwarts_direction.add_subordinate(Organization(department_name, responsible_names))

hogwarts.commit()

bank = Organization("Gringotts Wizarding Bank")

galleon = Currency("Galleon", "GLN")
# galleon.owner(None) # removes the ability to control the currency
galleon.commit()

for name in everyone:
    galleon.create(10, name)
galleon.create(1000000, bank)

muggle_money = Currency("Muggle money", "MGL")

muggle_money.create(10, "Harry Potter")
muggle_money.create(1000000, bank)
muggle_money.owner(bank)


world.commit()  # this should commit all underlying objects...


# make albus the 'Headmaster'
# harry_potter
# pay the fees of the school
# make the teachers the governors
# make different departments with different budgets (library, etc.)
# make a magic coin
