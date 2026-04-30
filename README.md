# Ransomware Simulator

A cybersecurity educational tool demonstrating how ransomware attacks work.

## ⚠️ Educational Use Only

This project is designed for **university cybersecurity education** purposes only. It simulates a ransomware attack in a controlled environment to help students understand:

- How ransomware encrypts files
- The importance of backups
- Cryptography concepts (AES-256)
- Defense strategies

## Requirements

```bash
pip install cryptography
```

## How to Run

```bash
python ransomware_sim.py
```

## Features

- **Auto-encryption**: Automatically encrypts files when run
- **AES-256 encryption**: Military-grade encryption
- **Password protection**: Decryption requires password
- **Cross-platform**: Works on Windows and Linux

## Password

- **Encrypt/Decrypt password**: `BANNANA`

## What It Does

1. Scans user files
2. Encrypts supported files (.txt, .pdf, .doc, .jpg, etc.)
3. Creates ransom note
4. Requires password to decrypt

## Important Notes

- ❌ Do NOT run on production systems
- ❌ Do NOT use on real data
- ✅ Use in isolated VM only
- ✅ For educational demonstrations only

## Disclaimer

This code is for **educational purposes only**. The author is not responsible for any misuse or damage caused by this program. Always use in a controlled, isolated environment (like a VM) for learning purposes only.
