# MultiCouriers
Project made for the UniBo course in Combinatorial Decision Making &amp; Optimization (2022/2023)

## Before running

First of all, make sure you install pipenv and that you install all dependencies with it

```shell
pip install pipenv
# (cd into the repo's directory)
pipenv install
pipenv shell # activate virtual environment
```

Then, use the newly installed `pysmt` package to install the z3 and MSAT solvers

```shell
pysmt-install --z3
pysmt-install --msat

pysmt-install --check # to make sure they both installed correcly 
```