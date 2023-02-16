# module imports
import hashlib
import hmac


def verify_hash(data, hash):
    # THIS SHOULD BE CONVERTED INTO AN ENVIROMENT VARIABLE
    bot_token = "6004606739:AAH3fMMPLiU2iC48xUWlSGGzcxHGQu_f200"
    key = hashlib.sha256(bot_token.encode()).digest()

    data_keys = list(data.keys())
    data_keys.remove("hash")
    data_keys.sort()
    data_string = []
    for k in data_keys:
        data_string.append(f"{k}={data.get(k)}")

    data_string = "\n".join(data_string)

    # Generate the hash.
    signature = hmac.new(
        key,
        data_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return signature == hash
