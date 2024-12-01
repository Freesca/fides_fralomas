#!/bin/bash


directories=(./*_microservice)

for dir in "${directories[@]}"; do
	echo "Installing pyenv in $dir"
	cd "$dir"
	python3 -m venv venv
	echo "Installint requirements in $dir"
	pyenv/bin/pip3 install -r requirements.txt
	echo "Done!"
	cd ..
done
