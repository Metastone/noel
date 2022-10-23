# Noel

A highly advanced piece of software to organize a random gift exchange. Made initially to be used for Christmas with my family.

- Takes a list of forbidden groups (groups of people that can't give gifts to one another)
- Takes a list of forbidden transaction ('person A' gives a gift to 'person B')

# Dependencies

- PyYAML (to load the program configuration)
- schema (to validate the program configuration)
- tqdm (for progress bar)

# Usage

```
usage: noel.py [-h] [--seed SEED]

Organize a gift exchange

options:
  -h, --help   show this help message and exit
  --seed SEED  Seed to use for random operations (integer). If not present, the current time is used.
```

# Output example

```
$ ./noel.py --seed 1812
INFO - Using the used-defined seed for random operations : 1812
INFO - Using the configuration file config.yml
INFO - Compute all solutions and choose one randomly...
INFO - 1705 solutions found                                                                                                                   
INFO - ********** SOLUTION **********
INFO - Christian  --> Julien
INFO - Claude     --> Hugo
INFO - Hugo       --> Christian
INFO - Isabelle   --> Claude
INFO - Jean       --> Lucie
INFO - Julien     --> Nicolas
INFO - Lucie      --> Jean
INFO - Marie      --> Isabelle
INFO - Nicolas    --> Marie
```

