# pyscaffoldext-uhnderstand

Get started making a python library quick

## Description

Do you need to share Uhnder python code with peers, other teams, or maybe even
customers?

Use pyscaffoldext-jaustinpage to jump-start your project FAST!

## How to use

First, Get a repo created for your library.

### Ubuntu Instructions

In a terminal

1. Install git
   ```shell
   sudo apt install git
   ```
1. Make a github folder
   ```shell
   mkdir -p ~/github
   ```
1. Clone the repo you got created for you
   ```shell
   git clone ssh://github.com/jaustinpage/<repo_name> ~/github/jaustinpage/<repo_name>
   ```
1. Install the PyScaffold jaustinpage extension (no virtualenv required)
   ```shell
   pip install --user --upgrade setuptools setuptools_scm wheel pip
   pip install --user --upgrade git+ssh://github.com/jaustinpage/pyscaffoldext-jaustinpage.git
   ```
1. Add boilerplate to the bare repo
   ```shell
   # pyscaffold uses git information to determine the project author information
   git config --global user.name "Peter Gibbons"
   git config --global user.email "Peter.Gibbons@innotech.com"
   # use pyscaffold to initialize the new repo.
   putup --venv --jaustinpage --force ~/github/<repo_name>
   ```

### Windows Instructions

1. Install [python](https://www.python.org/downloads/windows/). Use the download link
   for the latest python 3, windows 64bit installer. When you are installing, be sure to
   select:
   1. In Optional features: select Documentation, Pip, and Python test suite
   1. In Advanced Options: select "Create shortcuts" and "Add python to environment
      variables"
1. Create a githufolder in your "Documents" directory. We will use this to store github
   repos
1. Launch Powershell and run
   ```shell
   pip install --user --upgrade setuptools setuptools_scm wheel pip
   pip install --user --upgrade git+ssh://github.com/jaustinpage/pyscaffoldext-jaustinpage#egg=pyscaffoldext-jaustinpage
   ```
1. Add boilerplate to the bare repo
   ```shell
   # pyscaffold uses git information to determine the project author information
   git config --global user.name "Peter Gibbons"
   git config --global user.email "Peter.Gibbons@innotech.com"
   # use pyscaffold to initialize the new repo.
   putup --venv --uhnderstand --force Documents\github\<repo_name>
   ```

### Final Step - README.md in the new repo

Use the "Repo/Library Management Tasks -> First build" section of
`<repo_name>/README.md`the new repo to make your first two commits. These steps only
need to be done once.

Send feedback on this process to `jaustinpage@gmail.com`

## Features beyond PyScaffold

- PyCharm run configs
- Makefile for all-in-one test, lint, and build
- Automatic Import Sorting (using isort)
- Automatic Code Formatting (using black)
- PyScaffold set to --markdown by default
- Automatic Markdown formatting (using mdformat)
- Automatic Static Code analysis, aka "Linting" (using flake8 + one or two plugins)
- Automatic pytest Code Coverage enforcement to 100%

## Note

This project has been set up using PyScaffold 4.0.2. For details and usage information
on PyScaffold see https://pyscaffold.org/.
