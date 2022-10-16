import re
from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from stegano import lsb

# Randomizer byte number function
def get_bytes(n):
    random_number = 1000
    return random_number.to_bytes(n, "big")


# Global Variables for Layer 1 - RSA
rsa_public_key = RSA.import_key(open("keys/rsa_public_key.pem").read())
rsa_private_key = RSA.import_key(open("keys/rsa_private_key.pem").read())
rsa_encryptor = PKCS1_OAEP.new(rsa_public_key, randfunc=get_bytes)
rsa_decryptor = PKCS1_OAEP.new(rsa_private_key)

# Global Variables for Layer 2 - AES
with open("keys/aes_key.pem", "rb") as p:
    aes_key = p.read()
aes_encryptor = AES.new(aes_key, AES.MODE_EAX, nonce=b"123456")
aes_decryptor = AES.new(aes_key, AES.MODE_EAX, aes_encryptor.nonce)

# Global Variables for Layer 3 - 3DES
with open("keys/des3_key.pem", "rb") as p:
    des_key = p.read()
des_encryptor = DES3.new(des_key, DES3.MODE_EAX, nonce=b"123456")
des_decryptor = DES3.new(des_key, DES3.MODE_EAX, des_encryptor.nonce)

# Double Encryption Function
def encrypt(plaintext):

    # Generating ciphertext by passing through layer 1 using plaintext as input
    ciphertext = rsa_encryptor.encrypt(plaintext)

    # Generating ciphertext by passing through layer 2 using ciphertext from layer 1 as input
    ciphertext = aes_encryptor.encrypt(ciphertext)

    # Generating ciphertext by passing through layer 3 using ciphertext from layer 2 as input
    ciphertext = des_encryptor.encrypt(ciphertext)

    # Returning Ciphertext to called function
    return ciphertext


# Embedding text in a cover image using LSB technique
def hide(ciphertext):

    # Embedding ciphertext using Steganography using LSB technique
    embedded_image = lsb.hide("images/coverImage.png", str(ciphertext))

    # Saving the image as coverImageSecret.png with the embedded ciphertext
    embedded_image.save("images/coverImageSecret.png")


# Revealing hidden text from the steganographic image
def reveal():

    # Revealing the hidden ciphertext from coverImageSecret.png
    ciphertext = lsb.reveal("images/coverImageSecret.png")

    # Encoding the ciphertext to Byte format for decryption
    ciphertext = (
        ciphertext[2:-1].encode().decode("unicode_escape").encode("raw_unicode_escape")
    )


# Double Decryption Function
def decrypt(ciphertext):

    # Generating plaintext by passing through layer 3 using ciphertext as input
    plaintext = des_decryptor.decrypt(ciphertext)

    # Generating plaintext by passing through layer 2 using plaintext from layer 3 as input
    plaintext = aes_decryptor.decrypt(plaintext)

    # Generating plaintext by passing through layer 1 using plaintext from layer 2 as input
    plaintext = rsa_decryptor.decrypt(plaintext)

    # Returning plaintext to called function
    return plaintext


# Main Function
def main():

    # Receiving Plaintext from User
    plaintext = input("Enter plaintext: ")
    plaintext = bytes(plaintext, "utf-8")

    # Encrypting the plaintext using Double Encryption
    ciphertext = encrypt(plaintext)

    # Hiding the Double Encrypted ciphertext in a cover image
    hide(ciphertext)

    # Calling reveal() to reveal the hidden ciphertext in the coverImageSecret.png
    reveal()

    # Decrypting the obtained ciphertext from the steganographic image
    decrypted_plaintext = decrypt(ciphertext)
    decrypted_plaintext = plaintext.decode("utf-8")

    # Printing Plaintext after Double Decryption
    print(decrypted_plaintext)


# Calling the main function
main()
