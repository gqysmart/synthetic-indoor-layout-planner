import math

class Segment:
    def __init__(self):
        pass

    def get_start(self, points):
        raise NotImplementedError

    def get_end(self, points):
        raise NotImplementedError

class Line(Segment):
    def __init__(self, start_idx, end_idx):
        self.start_idx = start_idx
        self.end_idx = end_idx

    def get_start(self, points):
        return points[self.start_idx]

    def get_end(self, points):
        return points[self.end_idx]

class Arc(Segment):
    def __init__(self, start_idx, end_idx, center_idx, radius, start_angle, end_angle):
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.center_idx = center_idx
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def get_start(self, points):
        center = points[self.center_idx]
        return [
            center[0] + self.radius * math.cos(self.start_angle),
            center[1] + self.radius * math.sin(self.start_angle)
        ]

    def get_end(self, points):
        center = points[self.center_idx]
        return [
            center[0] + self.radius * math.cos(self.end_angle),
            center[1] + self.radius * math.sin(self.end_angle)
        ]

class Room:
    def __init__(self, points, outline):
        """
        Initialize Room with a list of points and outline as list of Line and Arc segments.
        Segments reference points by indices and must be linked head to tail to form a closed room.

        Args:
        points (list): List of [x, y] coordinates.
        outline (list): List of Line or Arc instances.
        """
        self.points = points
        if not outline:
            raise ValueError("Outline cannot be empty")
        if not points:
            raise ValueError("Points cannot be empty")
        for seg in outline:
            if isinstance(seg, Line):
                if seg.start_idx >= len(points) or seg.end_idx >= len(points):
                    raise ValueError("Invalid point index in Line")
            elif isinstance(seg, Arc):
                if seg.start_idx >= len(points) or seg.end_idx >= len(points) or seg.center_idx >= len(points):
                    raise ValueError("Invalid point index in Arc")
            else:
                raise ValueError("Invalid segment type")
        for i in range(len(outline) - 1):
            if not self._almost_equal(outline[i].get_end(points), outline[i+1].get_start(points)):
                raise ValueError(f"Segments {i} and {i+1} are not connected")
        if not self._almost_equal(outline[-1].get_end(points), outline[0].get_start(points)):
            raise ValueError("Outline is not closed")
        self.outline = outline

    def _almost_equal(self, p1, p2, tol=1e-6):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1]) < tol

if __name__ == "__main__":
    # Test with a rectangular room
    points = [[0, 0], [4, 0], [4, 3], [0, 3]]
    outlines = [
        Line(0, 1),
        Line(1, 2),
        Line(2, 3),
        Line(3, 0)
    ]
    room = Room(points, outlines)
    print("Room created successfully with rectangular outline.")

    # Test with arc
    points_arc = [[0, 0], [2, 0], [4, 2], [4, 0], [2, 2]]  # 4 is center
    outlines_arc = [
        Line(0, 1),
        Arc(1, 2, 4, 2, -math.pi/2, 0),  # from -pi/2 to 0 around [2,2]
        Line(2, 3),
        Line(3, 0)
    ]
    try:
        room_arc = Room(points_arc, outlines_arc)
        print("Room with arc created successfully.")
    except ValueError as e:
        print(f"Error creating room with arc: {e}")
