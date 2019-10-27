# Geom2D | Soccer Math

Geom is a Python library for dealing with math and geometry problems in SS2D.

## Installation

Use the this include to install Geom.

```python
from lib.math.soccer_math import *
```
Or
```python
from lib.math.soccer_math import *
```

## Usage

```python
from lib.math.soccer_math import *

vec1 = Vector2D() # create Vector with default value.
vec2 = Vector2D(20,30) # create Vector with 20 , 30 value directly.
l = Line2D(vec1,vec2) # create line from 2 points.
c = Circle2D(3,3,5) # create circle with center point and radius value.
print(c.intersection(line=l)) #  calculate the intersection with straight line.
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## TODO
triangulation | 
delaunay_triangulation | 
composite_region_2d | 
voronoi_diagram
