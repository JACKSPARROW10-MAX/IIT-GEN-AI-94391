def circle_area(radius):
    """Calculate the area of a circle given its radius."""
    import math
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius ** 2

def rectangle_area(length, width):
    """Calculate the area of a rectangle given its length and width."""
    if length < 0 or width < 0:
        raise ValueError("Length and width cannot be negative")
    return length * width

def triangle_area(base, height):
    """Calculate the area of a triangle given its base and height."""
    if base < 0 or height < 0:
        raise ValueError("Base and height cannot be negative")
    return 0.5 * base * height

def square_area(side):
    """Calculate the area of a square given its side length."""
    if side < 0:
        raise ValueError("Side length cannot be negative")
    return side ** 2

if __name__ == "__main__":
    print("Circle area with radius 5:", circle_area(5))
    print("Rectangle area with length 4 and width 6:", rectangle_area(4, 6))
    print("Triangle area with base 3 and height 7:", triangle_area(3, 7))
    print("Square area with side length 4:", square_area(4))