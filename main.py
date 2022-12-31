from fastapi import FastAPI, Response, status
from cryptography.fernet import Fernet
import motor.motor_asyncio
from bson.objectid import ObjectId
from fastapi.responses import PlainTextResponse
from schemas import CreateSecret, ValidateSecretPhrase


app = FastAPI()

ENCRYPT_KEY = b"Z6aqHbMH0zU4P_V-_ekdVHu02i6f15aPlQwsBM1tMbU="
MONGO_URL = "mongodb://root:root@mongo_db"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.keys


@app.get("/")
def main() -> None:
    """Root route."""
    return "FastAPI + Mongo"


@app.get("/keys")
async def all_keys() -> None:
    """Print all keys in DB."""
    keys = await db["keys"].find().to_list(100)
    print(keys)


@app.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate(body: CreateSecret) -> dict:
    """Generate a secret key."""
    fernet = Fernet(ENCRYPT_KEY)

    mongo = {
        "value": fernet.encrypt(body.secret_value.encode()),
        "phrase": str(hash(body.secret_phrase)),
        "is_used": False,
    }
    new_key = await db["keys"].insert_one(mongo)
    return {"result": str(new_key.inserted_id)}


@app.post("/secrets/{secret_key}", status_code=status.HTTP_200_OK)
async def get_secret(secret_key: str, body: ValidateSecretPhrase) -> str:
    """Get secret value by passphrase (secret_key)."""
    data = await db["keys"].find_one({"_id": ObjectId(secret_key)})

    if data is None:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This secret key does not exist.",
        )

    if data["is_used"]:
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Key has been used already.",
        )
    try:
        assert str(hash(body.secret_phrase)) == data["phrase"]
    except AssertionError:
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Passed phase is not valid.",
        )

    fernet = Fernet(ENCRYPT_KEY)
    decoded_value = fernet.decrypt(data["value"].decode())

    await db["keys"].update_one(
        {"_id": ObjectId(secret_key)}, {"$set": {"is_used": True}}
    )

    return decoded_value
