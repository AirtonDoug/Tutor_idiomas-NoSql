import motor.motor_asyncio

uri = "mongodb+srv://airton:airton@tutor-idiomas.mf0ub.mongodb.net/?retryWrites=true&w=majority&appName=Tutor-Idiomas"

# Create a new client and connect to the server
client = motor.motor_asyncio.AsyncIOMotorClient(uri)

# Helper function to get the database
def get_database():
    return client['tutor_idiomas']