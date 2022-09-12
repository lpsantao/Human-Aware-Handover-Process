import numpy as np
import open3d
from typing import Optional
from threading import Thread
import time


class Visualizer:
    """Visualizer Class."""

    def __init__(self):
        """Initialize Visualizer object."""
        self.pcd: Optional[open3d.geometry.PointCloud] = None
        self.bb: Optional[np.ndarray] = None
        self.vis: Optional[open3d.cpu.pybind.visualization.VisualizerWithKeyCallback] = None

    def visualizer3DOpen3d(self, points: Optional[np.ndarray], bb_points: Optional[np.ndarray], bb_lines: Optional[np.ndarray]) -> None:
        """Fill visualizer with the 3D data.

        Args:
            points (np.ndarray[np.float64]): Points to be plotted Shape=(N,3)
            bb_points (np.ndarray[np.float64]): Points from Bounding Box. Shape=(N,3)
            bb_lines (np.ndarray[np.float64]): Lines from Bounding Box. Shape=(12,1)
        """
        if self.pcd is None:
            self.pcd = open3d.geometry.PointCloud()
        if self.bb is None:
            self.bb = open3d.geometry.LineSet()

        if bb_points is not None:
            # create lineset
            self.bb.points = open3d.utility.Vector3dVector(bb_points)

        if bb_lines is not None:
            self.bb.lines = open3d.utility.Vector2iVector(bb_lines)
            self.bb.colors = open3d.utility.Vector3dVector(np.tile([0, 1, 0], [len(self.bb.lines), 1]))

        if points is not None:
            self.pcd.points = open3d.utility.Vector3dVector(np.float64(points))

    def show(self) -> None:
        """Show visualization."""
        if self.vis is None:

            resolution_width = 1280
            resolution_height = 720

            # Create cartesian coordinate
            FOR = open3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5, origin=[0, 0, 0])
            vis = open3d.visualization.VisualizerWithKeyCallback()
            vis.create_window(width=resolution_width, height=resolution_height)

            vis.add_geometry(FOR)
            vis.add_geometry(self.pcd)
            vis.add_geometry(self.bb)

            self.vis = vis
            view_ctl = self.vis.get_view_control()

            view_ctl.set_lookat((0.5, 0.5, 0.5))
            view_ctl.set_up((0, 0, 1))  # set the negative direction of the y-axis as the up direction
            view_ctl.set_front((1, 1, 1))  # s

        if self.pcd:
            self.vis.update_geometry(self.pcd)
        if self.bb:
            self.vis.update_geometry(self.bb)

        self.vis.poll_events()
        self.vis.update_renderer()

    def close(self):
        """Close Visualizer."""
        if self.vis:
            self.vis.close()


def test():
    # t2.start()
    v = Visualizer()

    points = np.float64([[0, 0, 1]])
    bb_lines = np.array([[0, 1], [1, 3], [3, 2], [2, 0], [0, 4], [1, 5], [3, 7], [2, 6], [4, 5], [5, 7], [7, 6],
                        [6, 4]])
    bb_points = np.array([[1.64, 1.12, 1.121],
                         [1.324, 0, 1.13],
                         [1.132, 1.134, 0],
                         [1.2224, 0, 0],
                         [0, 1.2321, 1.3234],
                         [0, 0, 1.12332],
                         [0, 1.3232, 0],
                         [0, 0, 0]])
    while True:
        for i in range(1,3):
            points_i = bb_points + 0.5
            bb_points= np.vstack((bb_points, points_i))

            lines_i = np.array([[0, 1], [1, 3], [3, 2], [2, 0], [0, 4], [1, 5], [3, 7], [2, 6], [4, 5], [5, 7], [7, 6],
                            [6, 4]]) + 8 * i
            bb_lines=np.vstack((bb_lines,lines_i))
        print(bb_lines)
        print(bb_points)

        for j in range(2000):

            # Define points to be plotted
            points = points+0.1

            v.visualizer3DOpen3d(points, bb_points=bb_points, bb_lines=bb_lines)
            v.show()
            time.sleep(0.1)


