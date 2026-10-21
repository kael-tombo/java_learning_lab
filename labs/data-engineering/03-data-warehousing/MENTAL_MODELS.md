# Mental Models for Data Warehousing

## 1. The Library Model
- **Facts** = Books on shelves (measurable events)
- **Dimensions** = Catalog system (how to find books)
- **Star Schema** = Subject-organized sections
- **OLAP Cube** = Multi-dimensional cross-reference

## 2. The Rubik's Cube
Each axis represents a dimension. Rotating the cube changes the analytical perspective. Drilling down zooms into a smaller cube face.

## 3. The City Map
- **Fact Tables** = Intersections (where events happen)
- **Dimensions** = Street names, neighborhoods, zones (attributes)
- **Hierarchies** = Country -> State -> City -> Zip
- **Grain** = Map scale (zoom level)

## 4. The Filing Cabinet
- Each drawer = Data mart (Sales, Finance, HR)
- Each folder = Dimension
- Each document = Fact record
- Cross-reference index = Conformed dimensions
