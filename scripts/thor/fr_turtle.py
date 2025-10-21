import turtle

with open("turtle", "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("Avance"):
            parts = line.split()
            distance = int(parts[1])
            turtle.forward(distance)
        elif line.startswith("Tourne gauche"):
            parts = line.split()
            angle = int(parts[3])
            turtle.left(angle)
        elif line.startswith("Tourne droite"):
            parts = line.split()
            angle = int(parts[3])
            turtle.right(angle)
        elif line.startswith("Recule"):
            parts = line.split()
            distance = int(parts[1])
            turtle.backward(distance)
turtle.done()
