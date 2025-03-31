# Parker²

This repository contains brute-force tools designed to search for a 3x3 magic square of squares. The chances of successfully finding one using these methods are extremely, incredibly, **astronomically** low. However, given a sufficiently large search range, an unimaginable amount of time (think the lifespan of the universe), and an extraordinary stroke of luck, one of these approaches *might* just succeed.

A magic square of squares is similar to a regular [magic square](https://en.wikipedia.org/wiki/Magic_square), except that all of its values are perfect squares. These squares gained popularity in 2016 after a series of [Numberphile](https://www.youtube.com/@numberphile) videos, in which a failed attempt was humorously dubbed the "[Parker square](https://www.youtube.com/watch?v=aOT_bG-vWyg)" hence the repository name.

## Requirements

A list of requirements to compile and use these tools:

- build-essential (g++, make)
- GMP (GNU Multiple Precision Arithmetic Library)
- Python 3+

Installation (Linux / Ubuntu):

```bash
sudo apt-get install build-essential libgmp-dev python3
```

## Best result so far

The most successful outcome so far was obtained after a couple of minutes using the random root method. It discovered a "magic" square of squares in which all values, except those in the bottom row, are perfect squares.

```math
\begin{matrix}
46²    &   50²  &   74²  \\
82²    &   58²  &   2²   \\
√1252² & √4228² & √4612² \\
\end{matrix}
```

A list of weight $(x, y, z)$ that would result ins similar imperfect magic squares

| x    | y     | z     |
| ---- | ----- | ----- |
| 3364 | 1248  | -2112 |
| 1369 | 1248  | 408   |
| 7569 | 2808  | -4752 |
| 841  | -528  | 312   |

## Brute force methods

### Random Search

#### Theory

This brute force approach is as stupid as it can be. A compiled C++ binary generates a set of nine unique random numbers, squares them, and checks if they form a valid magic square. If not, the process repeats - indefinitely. A Python wrapper handles multithreading and logs any successful squares found.

The main idea behind this approach was:
> COMPUTER = FAST

But as it turns out computer not fast enough... With a search range of 0 to 500 over eight hours, it completed 2.2 quadrillion iterations without finding a single magic square, not even an imperfect one. However, when the search is reduced to a range of 0 to 50, it quickly finds imperfect squares where all rows and one column add up correctly, but nothing beyond that.

#### Algorithm

This algorithm generates a set of nine unique random numbers, squares them, and checks if they form a valid magic square. Repeat forever. That's it!

#### Performance

- Ryzen 7 3700X: ~280 billion iterations per hour

### Random Root

#### Theory

This method begins with an already functional magic square. It then verifies whether the values within the magic square are themselves perfect squares. This process transforms a working magic square into a "precursor" that has the potential to consist entirely of perfect squares. A C++ binary is used for generating and testing the squares, while a Python wrapper handles multithreading and logging.

#### Algorithm

This algorithm generates a set of three unique random weights $(x, y, z)$, with the first weight $(x)$ always being positive. These weights are then applied to this set of equations to construct a working (normal) 3x3 magic square.

```math
\begin{matrix}
  x - y   & x + y + z &   x - z   \\
x + y - z &     x     & x - y - z \\
  x + z   & x - y - z &   x + y
\end{matrix}
```

Each value in the square is checked to ensure it is positive, and its square root is taken to determine if it is a perfect square. If all values meet these criteria, a magic square of squares has been successfully found.

#### Performance

- Ryzen 7 3700X: ~1.45 trillion iterations per hour