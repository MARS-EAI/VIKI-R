import cv2
import numpy as np
import argparse


def parse_points(s: str):
    """
    Parse a string of points in the format "x1,y1;x2,y2;...@x3,y3;x4,y4;..."
    into a list of lists of (x, y) integer tuples.
    Each line is separated by @ symbol.
    """
    lines = []
    for line in s.split('@'):
        if not line:
            continue
        pts = []
        for part in line.split(';'):
            if not part:
                continue
            x_str, y_str = part.split(',')
            pts.append((int(x_str), int(y_str)))
        if pts:
            lines.append(pts)
    return lines


def draw_lines_on_image(input_path: str, lines: list,
                        output_path: str, colors: list = None,
                        thicknesses: list = None):
    """
    Draw multiple smooth anti-aliased lines on the image.

    Args:
        input_path: Path to the source image file.
        lines: List of lists of (x, y) tuples, each list represents a line.
        output_path: Path where to save the resulting image.
        colors: List of BGR color tuples for each line (default: all green).
        thicknesses: List of thickness values for each line (default: all 2 pixels).
    """
    # Read the image
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {input_path}")

    # Set default colors and thicknesses if not provided
    if colors is None:
        colors = [(0, 255, 0)] * len(lines)  # Default green
    if thicknesses is None:
        thicknesses = [2] * len(lines)  # Default thickness 2

    # Draw each line
    for line, color, thickness in zip(lines, colors, thicknesses):
        # Convert points to numpy array of shape (-1, 1, 2)
        pts_array = np.array(line, dtype=np.int32).reshape((-1, 1, 2))

        # Draw polyline with anti-aliasing
        cv2.polylines(img, [pts_array], isClosed=False, color=color,
                      thickness=thickness, lineType=cv2.LINE_AA)

        # Optionally draw circles at each point for visual emphasis
        for pt in line:
            cv2.circle(img, pt, radius=max(thickness+1, 4), color=color,
                       thickness=-1, lineType=cv2.LINE_AA)

    # Save output
    cv2.imwrite(output_path, img)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Draw multiple smooth lines on an image.')
    parser.add_argument('input_image', help='Path to the input image file')
    parser.add_argument('points', 
                        help='Coordinates in "x1,y1;x2,y2;...@x3,y3;x4,y4;..." format. '
                             'Use @ to separate different lines.')
    parser.add_argument('output_image', help='Path to save the output image')
    parser.add_argument('--colors', default=None,
                        help='Line colors as "B1,G1,R1;B2,G2,R2;..." (default: all green)')
    parser.add_argument('--thicknesses', default=None,
                        help='Line thicknesses as "t1,t2,..." (default: all 2)')
    args = parser.parse_args()

    # Parse the points
    lines = parse_points(args.points)

    # Parse colors if provided
    colors = None
    if args.colors:
        colors = []
        for color_str in args.colors.split(';'):
            b, g, r = map(int, color_str.split(','))
            colors.append((b, g, r))

    # Parse thicknesses if provided
    thicknesses = None
    if args.thicknesses:
        thicknesses = list(map(int, args.thicknesses.split(',')))

    draw_lines_on_image(
        args.input_image,
        lines,
        args.output_image,
        colors=colors,
        thicknesses=thicknesses
    )

    print(f"Output image saved to {args.output_image}")
