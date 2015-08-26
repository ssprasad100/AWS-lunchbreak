COST_GROUP_ALWAYS = 0
COST_GROUP_ADDITIONS = 1

COST_GROUP_CALCULATIONS = (
    (COST_GROUP_ALWAYS, 'Altijd de groepsprijs'),
    (COST_GROUP_ADDITIONS, 'Duurder bij toevoegen, zelfde bij aftrekken')
)

ICONS = (
    (0, 'Onbekend'),
    # 1xx StoreCategories
    (100, 'Slager'),
    (101, 'Bakker'),
    (102, 'Broodjeszaak'),
    # 2xx Ingredients
    (200, 'Tomaten'),
    # 3xx FoodTypes
    (300, 'Broodje')
)

DAYS = (
    (0, 'Zondag'),
    (1, 'Maandag'),
    (2, 'Dinsdag'),
    (3, 'Woensdag'),
    (4, 'Donderdag'),
    (5, 'Vrijdag'),
    (6, 'Zaterdag')
)

INPUT_AMOUNT = 0
INPUT_SI_VARIABLE = 1
INPUT_SI_SET = 2

INPUT_TYPES = (
    (INPUT_AMOUNT, 'Aantal'),
    (INPUT_SI_VARIABLE, 'Aanpasbaar o.b.v. SI-eenheid'),
    (INPUT_SI_SET, 'Vaste hoeveelheid o.b.v. SI-eenheid'),
)

TOKEN_IDENTIFIER_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz0123456789'
TOKEN_IDENTIFIER_LENGTH = 64
