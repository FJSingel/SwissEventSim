# SwissEventSim
A script to simulate MTG tournament metagames

It takes input in the form of a CSV formatted like the one included in this project.
Draw pcts are encoded by having 2 win pcts totaling under 100. EX: a 50/45 MU has a 5% draw rate
Meta population is encoded with a % share (ex: 10.25%) or a hard count (EX: #1) on the diagonal
Currently there are no draws for mirrors; that would require input refactoring
