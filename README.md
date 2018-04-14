# CS188 Contest 2 Infrastructure

Visualize matches, random map layouts, and ranking analysis.

## Basic Instructions
- Students must edit `myTeam.py`
- To run a match, execute `python2.7 capture.py -r [RED TEAM FILE] -b [BLUE TEAM FILE] -l RANDOM -q`
    - `-q`: quiet mode
    - `-l`: layout mode
- Ranking analysis code is in `rank.py` and `rank_analysis.py`

## Useful EC2 Commands
- `scp -i <key pem file> /path/to/file ec2-user@public-DNS-of-ec2-instance:~/`
- `ssh -i <key pem file> ec2-user@public-DNS-of-ec2-instance`
