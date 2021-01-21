#!/bin/sh

# Decrypt the file
# mkdir $HOME/secrets
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$FIRESTORE_PASSPHRASE" \
--output ../firestore-access.json firestore-access.json.gpg
