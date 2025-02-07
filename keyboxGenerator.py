import os
from random import randint, choice
from base64 import b64decode

try:
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
except:
    pass

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)
LB = 2
UB = 12
CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
keyboxFormatter = """<?xml version="1.0"?>
<AndroidAttestation>
<NumberOfKeyboxes>1</NumberOfKeyboxes>
<Keybox DeviceID="{0}">
<Key algorithm="ecdsa">
<PrivateKey format="pem">
{1}</PrivateKey>
<CertificateChain>
<NumberOfCertificates>1</NumberOfCertificates>
<Certificate format="pem">
{2}</Certificate>
</CertificateChain>
</Key>
<Key algorithm="rsa">
<PrivateKey format="pem">
{3}</PrivateKey>
</Key>
</Keybox>
</AndroidAttestation>
"""


def canOverwrite(flags: list, idx: int, prompts: str | tuple | list | set) -> bool:
    if (
        isinstance(flags, list)
        and isinstance(idx, int)
        and -len(flags) <= idx < len(flags)
        and isinstance(prompts, (str, tuple, list, set))
    ):
        try:
            if isinstance(prompts, str):
                print('"{0}"'.format(prompts))
                choice = input("The file mentioned above exists. Overwrite or not [aYn]? ")
            else:
                print(prompts)
                choice = input(
                    "At least one of the files mentioned above exists. Overwrite or not [aYn]? "
                )
            if choice.upper() == "A":
                for i in range(
                    (idx if idx >= 0 else len(flags) + idx), len(flags)
                ):  # overwirte the current file and all the following necessary files no matter whether they exist
                    flags[i] = True
                return True
            elif choice.upper() == "N":
                return False
            else:
                flags[idx] = True
                return True
        except BaseException as e:
            print(e)
            return False
    else:
        input("#")
        return False


def execute(commandline: str) -> int | None:
    if isinstance(commandline, str):
        print("$ " + commandline)
        return os.system(commandline)
    else:
        return None


def handleOpenSSL(flag: bool = True) -> bool | None:
    if isinstance(flag, bool):
        errorLevel = execute("openssl version")
        if EXIT_SUCCESS == errorLevel:
            return True
        elif flag:  # can try again
            execute("sudo apt-get install openssl libssl-dev")
            return handleOpenSSL(False)
        else:
            return False
    else:
        return None


def pressTheEnterKeyToExit(errorLevel: int | None = None):
    try:
        print(
            "Please press the enter key to exit ({0}). ".format(errorLevel)
            if isinstance(errorLevel, int)
            else "Please press the enter key to exit. "
        )
        input()
    except:
        pass

def generate_keybox(ecPrivateKeyFilePath, certificateFilePath, rsaPrivateKeyFilePath):
    failureCount = 0
    deviceID = "".join([choice(CHARSET) for _ in range(randint(LB, UB))])
    # First-phase Generation #
    failureCount += (
        execute(
            'openssl ecparam -name prime256v1 -genkey -noout -out "{0}"'.format(
                ecPrivateKeyFilePath
            )
        )
        != 0
    )
    failureCount += (
        execute(
            'openssl req -new -x509 -key "{0}" -out {1} -days 3650 -subj "/CN=Keybox"'.format(
                ecPrivateKeyFilePath, certificateFilePath
            )
        )
        != 0
    )
    failureCount += (
        execute('openssl genrsa -out "{0}" 2048'.format(rsaPrivateKeyFilePath)) != 0
    )
    if failureCount > 0:
      return "Error: Cannot generate a sample ``keybox.xml`` file since {0} PEM file{1} not generated successfully. ".format(
            failureCount, ("s were" if failureCount > 1 else " was")
        )

    # First-phase Reading #
    try:
        with open(ecPrivateKeyFilePath, "r", encoding="utf-8") as f:
            ecPrivateKey = f.read()
        with open(certificateFilePath, "r", encoding="utf-8") as f:
            certificate = f.read()
        with open(rsaPrivateKeyFilePath, "r", encoding="utf-8") as f:
            rsaPrivateKey = f.read()
    except BaseException as e:
        return "Error: Failed to read one or more of the PEM files. Details are as follows. \n{0}".format(
            e
        )

    # Second-phase Generation #
    if rsaPrivateKey.startswith("-----BEGIN PRIVATE KEY-----") and rsaPrivateKey.rstrip().endswith(
        "-----END PRIVATE KEY-----"
    ):
        print(
            "A newer openssl version is used. The RSA private key in the PKCS8 format will be converted to that in the PKCS1 format soon. "
        )
        failureCount += execute(
            'openssl rsa -in "{0}" -out "{0}" -traditional'.format(rsaPrivateKeyFilePath)
        )
        if failureCount > 0:
          return "Error: Cannot convert the RSA private key in the PKCS8 format to that in the PKCS1 format. "
        else:
            print(
                "Finished converting the RSA private key in the PKCS8 format to that in the PKCS1 format. "
            )
            try:
                with open(rsaPrivateKeyFilePath, "r", encoding="utf-8") as f:
                    rsaPrivateKey = f.read()
            except BaseException as e:
              return 'Error: Failed to update the RSA private key from "{0}". Details are as follows. \n{1}'.format(
                    rsaPrivateKeyFilePath, e
                )
    elif rsaPrivateKey.startswith(
        "-----BEGIN OPENSSH PRIVATE KEY-----"
    ) and rsaPrivateKey.rstrip().endswith("-----END OPENSSH PRIVATE KEY-----"):
        print(
            "An OpenSSL private key is detected, which will be converted to the RSA private key soon. "
        )
        failureCount += execute(
            'ssh-keygen -p -m PEM -f "{0}" -N ""'.format(rsaPrivateKeyFilePath)
        )
        if failureCount > 0:
          return "Error: Cannot convert the OpenSSL private key to the RSA private key. "
        else:
            print("Finished converting the OpenSSL private key to the RSA private key. ")
            try:
                with open(
                    rsaPrivateKeyFilePath, "r", encoding="utf-8"
                ) as f:  # the ``ssh-keygen`` overwrites the file though no obvious output filepaths specified
                    rsaPrivateKey = f.read()
            except BaseException as e:
              return 'Error: Failed to update the RSA private key from "{0}". Details are as follows. \n{1}'.format(
                    rsaPrivateKeyFilePath, e
                )

    # Brief Checks #
    if not (
        ecPrivateKey.startswith("-----BEGIN EC PRIVATE KEY-----")
        and ecPrivateKey.rstrip().endswith("-----END EC PRIVATE KEY-----")
    ):
        return "Error: An invalid EC private key is detected. Please try to use the latest key generation tools to solve this issue. "
    if not (
        certificate.startswith("-----BEGIN CERTIFICATE-----")
        and certificate.rstrip().endswith("-----END CERTIFICATE-----")
    ):
      return "Error: An invalid certificate is detected. Please try to use the latest key generation tools to solve this issue. "
    if not (
        rsaPrivateKey.startswith("-----BEGIN RSA PRIVATE KEY-----")
        and rsaPrivateKey.rstrip().endswith("-----END RSA PRIVATE KEY-----")
    ):
      return "Error: An invalid final RSA private key is detected. Please try to use the latest key generation tools to solve this issue. "

    # Keybox Generation #
    keybox = keyboxFormatter.format(deviceID, ecPrivateKey, certificate, rsaPrivateKey)
    return keybox

def main(
    ecPrivateKeyFilePath: str = "ecPrivateKey.pem",
    certificateFilePath: str = "certificate.pem",
    rsaPrivateKeyFilePath: str = "rsaPrivateKey.pem",
    keyboxFilePath: str = "keybox.xml",
) -> str:
    # Generate Keybox (using helper function)
    keybox_content = generate_keybox(ecPrivateKeyFilePath, certificateFilePath, rsaPrivateKeyFilePath)
    if keybox_content.startswith("Error"):
        return keybox_content  # Return error message

    # Write to file if no errors and path is provided.
    if keyboxFilePath:
        try:
            with open(keyboxFilePath, "w", encoding="utf-8") as f:
                f.write(keybox_content)
            return f"Successfully wrote the keybox to {keyboxFilePath}."

        except Exception as e:
          return f"Failed to write the keybox to {keyboxFilePath}. Details:\n{e}"
    else:
       return keybox_content # if keyboxFilePath not provided return the generated key
