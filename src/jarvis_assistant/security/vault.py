from __future__ import annotations

from pathlib import Path

from cryptography.fernet import Fernet


class EncryptedKeyVault:
    def __init__(self, key_file: Path, data_file: Path) -> None:
        self.key_file = key_file
        self.data_file = data_file
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_fernet(self) -> Fernet:
        if not self.key_file.exists():
            self.key_file.write_bytes(Fernet.generate_key())
        return Fernet(self.key_file.read_bytes())

    def store(self, key: str, value: str) -> None:
        fernet = self._get_fernet()
        line = f"{key}:{value}".encode("utf-8")
        token = fernet.encrypt(line)
        with self.data_file.open("ab") as fh:
            fh.write(token + b"\n")
