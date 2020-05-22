#!/bin/sh

for I in ../docker-compose/*.yml; do
	BASENAME="${I##*/}" NAME="${BASENAME%.yml}"
	kompose convert -f "${I}" -o "${NAME}"
done
