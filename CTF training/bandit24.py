bandit24_pass = "VAfGXJ1PBSsPSnvsjI8p759leLZ9GGar"
with open('list.txt', 'w') as file:
    for i in range(0, 9999):
        file.write('{} {}\n'.format(bandit24_pass, str(i).zfill(4)))