#!/bin/sh

mv transcript-curr.out transcript-old.out
../mnvc transcript > transcript-curr.out
diff transcript-curr.out transcript-old.out

