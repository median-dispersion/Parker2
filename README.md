# Parker²

This repository contains brute-force tools designed to search for a 3x3 magic square of squares. The chances of successfully finding one using these methods are extremely, incredibly, **astronomically** low. However, given a sufficiently large search range, an unimaginable amount of time (think the lifespan of the universe), and an extraordinary stroke of luck, one of these approaches *might* just succeed.

A magic square of squares is similar to a regular [magic square](https://en.wikipedia.org/wiki/Magic_square), except that all of its values are perfect squares. These squares gained popularity in 2016 after a series of [Numberphile](https://www.youtube.com/@numberphile) videos, in which a failed attempt was humorously dubbed the "[Parker square](https://www.youtube.com/watch?v=aOT_bG-vWyg)" hence the repository name.

## Requirements

This repository was developed and tested on Debian and requires the following packages to be installed:

- git
- [Docker](https://www.docker.com/)

### Install packages

```sh
sudo apt-get install git
```

### Install Docker

For installing Docker, please refer to the official documentation:

- [Install Docker Engine](https://docs.docker.com/engine/install/)
- [Install Docker Engine on Debian](https://docs.docker.com/engine/install/debian/)

## Alternative approaches

You can find a bunch of older, less efficient search approaches under the [branches](https://github.com/median-dispersion/Parker2/branches) section of this repository. These were either slower or less reliable than the ones in this branch and are only kept for reference.