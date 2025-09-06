Parker²

# Parker²

This repository contains brute-force tools designed to search for a 3x3 magic square of squares. The chances of successfully finding one using these methods are extremely, incredibly, **astronomically** low. However, given a sufficiently large search range, an unimaginable amount of time (think the lifespan of the universe), and an extraordinary stroke of luck, one of these approaches *might* just succeed.

A magic square of squares is similar to a regular [magic square](https://en.wikipedia.org/wiki/Magic_square), except that all of its values are perfect squares. These squares gained popularity in 2016 after a series of [Numberphile](https://www.youtube.com/@numberphile) videos, in which a failed attempt was humorously dubbed the "[Parker square](https://www.youtube.com/watch?v=aOT_bG-vWyg)" hence the repository name.

## Requirements

A list of requirements to compile and use these tools:

- git
- build-essential (g++, make)
- Python 3+ (python3, python3-pip)

Installation Linux (Debian / Ubuntu):

```bash
sudo apt-get install git build-essential python3 python3-pip
```

Install required Python packages:

```bash
pip install -r requirements.txt
```