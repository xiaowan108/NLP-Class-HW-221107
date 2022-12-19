import os
path = "Plant"
for root, dirs, files in os.walk(path):
    for name in files:
        if name.endswith(".txt"):
            print(os.path.join(root, name))