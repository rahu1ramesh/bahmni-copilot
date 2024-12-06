#!/bin/bash

file='.git/hooks/pre-commit'
gitFolder='.git'
if [ ! -d $gitFolder ]
then
    echo 'git not initialised'

elif [ ! -f $file ]
then
    echo 'No Talisman hook available. Setting up the hook now..'
    echo 'Copying Talisman pre-commit hook to your git hooks'
    curl -L https://thoughtworks.github.io/talisman/install.sh -o ~/install-talisman.sh
    chmod +x ~/install-talisman.sh

    ~/install-talisman.sh pre-commit
else
    echo 'A pre-commit hook already exists.'
fi