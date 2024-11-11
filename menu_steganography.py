# -*- coding: utf-8 -*-
"""Menu steganography.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ceJsIJQsx1sehuCWFVoQq0jXgsEGbJ2V
"""

#importando as bibliotecas necessarias
from google.colab import files
from PIL import Image
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import hashlib
import os

# Primeiro, instale as bibliotecas necessárias
!pip install Pillow cryptography

# Função para converter uma string em binário
def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

# Função para converter binário em uma string
def binary_to_message(binary_data):
    binary_chars = [binary_data[i:i + 8] for i in range(0, len(binary_data), 8)]
    return ''.join(chr(int(binary_char, 2)) for binary_char in binary_chars)

# Função para embutir texto em uma imagem
def encode_message(image_path, message, output_image_path):
    image = Image.open(image_path)
    image = image.convert('RGB')
    pixels = image.load()

    binary_message = message_to_binary(message) + '1111111111111110'  # Delimitador
    data_index = 0

    for row in range(image.size[1]):
        for col in range(image.size[0]):
            if data_index < len(binary_message):
                r, g, b = pixels[col, row]
                r = (r & 254) | int(binary_message[data_index])
                data_index += 1
                if data_index < len(binary_message):
                    g = (g & 254) | int(binary_message[data_index])
                    data_index += 1
                if data_index < len(binary_message):
                    b = (b & 254) | int(binary_message[data_index])
                    data_index += 1
                pixels[col, row] = (r, g, b)

    output_image_path = output_image_path + '.png'
    image.save(output_image_path)

    # Espera para garantir que a imagem esteja salva antes de iniciar o download

    print("\nO aquivo será baixado após finalizar a aplicação")
    files.download(output_image_path)

    print(f'\nMensagem embutida e imagem salva como {output_image_path}')

# Função para recuperar mensagem de uma imagem
def decode_message(image_path):
    image = Image.open(image_path)
    image = image.convert('RGB')
    pixels = image.load()

    binary_message = ''
    for row in range(image.size[1]):
        for col in range(image.size[0]):
            r, g, b = pixels[col, row]
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

    hidden_message = binary_to_message(binary_message)
    termination_index = hidden_message.find('ÿþ')  # Delimitador
    if termination_index != -1:
        hidden_message = hidden_message[:termination_index] if termination_index != -1 else hidden_message
    return hidden_message

# Função para gerar chaves pública e privada
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    # Salvando as chaves em arquivos
    with open("private_key.pem", "wb") as priv_file:
        priv_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open("public_key.pem", "wb") as pub_file:
        pub_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    return private_key, public_key

# Função para carregar chaves pública e privada
def load_keys():
    with open("private_key.pem", "rb") as priv_file:
        private_key = serialization.load_pem_private_key(
            priv_file.read(),
            password=None,
            backend=default_backend()
        )
    with open("public_key.pem", "rb") as pub_file:
        public_key = serialization.load_pem_public_key(
            pub_file.read(),
            backend=default_backend()
        )
    return private_key, public_key

# Função para encriptar mensagem
def encrypt_message(public_key, message):
    ciphertext = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# Função para decriptar mensagem
def decrypt_message(private_key, ciphertext):
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext.decode()

# Função para gerar o hash de uma imagem
def generate_hash(image_path):
    hash_md5 = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Função para baixar a chave privada
def download_private_key():
    if os.path.exists("private_key.pem"):
        print("\nO aquivo da chave privada será baixado após finalizar a aplicação")
        files.download("private_key.pem")
    else:
        print("\nA chave privada não foi encontrada.")

# Função principal para menu
def main_menu():
    if os.path.exists("private_key.pem") and os.path.exists("public_key.pem"):
        private_key, public_key = load_keys()
    else:
        private_key, public_key = generate_keys()

    while True:
        print("\nMenu de Opções:")
        print("(1) Embutir texto em uma imagem")
        print("(2) Recuperar texto inserido em uma imagem")
        print("(3) Gerar o hash das imagens e verificar alterações")
        print("(4) Encriptar a mensagem original e embutir na imagem")
        print("(5) Extrair e decriptar a mensagem encriptada de uma imagem")
        print("(S) Sair")

        choice = input("\nEscolha uma opção: ").strip().lower()

        match choice:
            case '1':
                print("\nInsira a imagem: ")
                uploaded = files.upload()
                image_path = list(uploaded.keys())[0]

                message = input("Texto a embutir: ")
                output_image_path = input("\nNome para a imagem alterada:")
                encode_message(image_path, message, output_image_path)

            case '2':
                print("\nInsira a imagem: ")
                uploaded = files.upload()
                image_path = list(uploaded.keys())[0]

                hidden_message = decode_message(image_path)

                print("\nMensagem recuperada:", hidden_message)

            case '3':
                print("\nInsira a imagem original: ")
                uploaded_original = files.upload()
                original_image_path = list(uploaded_original.keys())[0]

                print("\nInsira a imagem alterada: ")
                uploaded_altered = files.upload()
                altered_image_path = list(uploaded_altered.keys())[0]

                original_hash = generate_hash(original_image_path)
                altered_hash = generate_hash(altered_image_path)

                print("\nHash da imagem original:", original_hash)
                print("\nHash da imagem alterada:", altered_hash)

                if original_hash == altered_hash:
                    print("\nAs imagens são idênticas, sem alterações detectadas.")
                else:
                    print("\nAs imagens são diferentes, há alterações nos pixels.")

            case '4':
                message = input("Mensagem original: ")
                ciphertext = encrypt_message(public_key, message)

                print("\nMensagem encriptada (em bytes):", ciphertext)

                # Optionally, embutir a mensagem encriptada na imagem
                print("\nInsira a imagem: ")
                uploaded = files.upload()
                image_path = list(uploaded.keys())[0]
                output_image_path = input("\nNome para a imagem alterada:")

                encode_message(image_path, ciphertext.hex(), output_image_path)

                # Baixar a chave privada após baixar a imagem
                baixar_chave = input("\nDeseja baixar o arquivo da chave privada utilizada(s/n)? ").strip().lower()

                if baixar_chave == 's':
                  download_private_key()

            case '5':
                print("\nInsira a imagem: ")
                uploaded = files.upload()
                image_path = list(uploaded.keys())[0]

                use_custom_key = input("\nDeseja adicionar um arquivo de chave privada para descriptografar (s/n)? ").strip().lower()

                if use_custom_key == 's':
                    print("\nInsira o arquivo de chave privada: ")
                    uploaded_key = files.upload()
                    private_key_path = list(uploaded_key.keys())[0]
                    with open(private_key_path, "rb") as key_file:
                        private_key = serialization.load_pem_private_key(
                            key_file.read(),
                            password=None,
                            backend=default_backend()
                        )

                encrypted_message = decode_message(image_path)

                try:
                    # Convertendo a mensagem de hexadecimal para bytes
                    decrypted_message = decrypt_message(private_key, bytes.fromhex(encrypted_message))
                    print("\nMensagem decriptada:", decrypted_message)

                except Exception as e:
                    print("\nErro ao decriptar a mensagem:", e)

            case 's':
                print("\nSaindo...")
                break

            case _:
                print("\nOpção inválida. Selecione uma opção de 1 a 5.")

# Executar o menu principal
if __name__ == "__main__":
    main_menu()