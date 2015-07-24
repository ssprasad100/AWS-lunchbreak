
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

ORDER_STATUS_PLACED = 0
ORDER_STATUS_DENIED = 1
ORDER_STATUS_RECEIVED = 2
ORDER_STATUS_STARTED = 3
ORDER_STATUS_WAITING = 4
ORDER_STATUS_COMPLETED = 5
ORDER_STATUS_NOT_COLLECTED = 6

ORDER_STATUS = (
    (ORDER_STATUS_PLACED, 'Placed'),
    (ORDER_STATUS_DENIED, 'Denied'),
    (ORDER_STATUS_RECEIVED, 'Received'),
    (ORDER_STATUS_STARTED, 'Started'),
    (ORDER_STATUS_WAITING, 'Waiting'),
    (ORDER_STATUS_COMPLETED, 'Completed'),
    (ORDER_STATUS_NOT_COLLECTED, 'Not collected')
)

ORDER_ENDED = [
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_DENIED,
    ORDER_STATUS_NOT_COLLECTED
]
