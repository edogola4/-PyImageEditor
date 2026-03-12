"""Font style classification from image pixels."""
import cv2
import numpy as np


class FontStyleClassifier:
    """
    Classifies the visual style of text in an image region
    into one of five categories using pixel analysis only.
    Never uses hardcoded assumptions about the image content.
    """

    SCRIPT = "script"     # cursive, handwriting, calligraphy
    SERIF = "serif"       # Times-like, has serifs
    SANS = "sans"         # Arial-like, no serifs
    MONO = "mono"         # fixed-width, Courier-like
    DISPLAY = "display"   # decorative, ornamental

    def __init__(self, region_array: np.ndarray, block_height: int):
        self.region = region_array
        self.height = block_height
        self.gray = cv2.cvtColor(region_array, cv2.COLOR_RGB2GRAY)
        _, self.binary = cv2.threshold(
            self.gray, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        if self.binary.sum() == 0:
            _, self.binary = cv2.threshold(
                self.gray, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

    def classify(self) -> str:
        scores = {
            self.SCRIPT: self._score_script(),
            self.SERIF: self._score_serif(),
            self.SANS: self._score_sans(),
            self.MONO: self._score_mono(),
            self.DISPLAY: self._score_display(),
        }
        return max(scores, key=scores.get)

    def _score_script(self) -> float:
        """
        Script/cursive fonts have:
        - Highly connected strokes (few separate contours)
        - High stroke curvature
        - Varying stroke width (thick to thin transitions)
        - Diagonal dominant orientation
        - Low horizontal projection regularity
        """
        score = 0.0

        contours, _ = cv2.findContours(
            self.binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Script text has fewer, larger connected components
        # because letters connect to each other
        total_pixels = self.binary.sum() / 255
        if total_pixels == 0:
            return 0.0

        if len(contours) > 0:
            areas = [cv2.contourArea(c) for c in contours]
            avg_area = np.mean(areas)
            # Large average contour area = connected script
            if avg_area > total_pixels * 0.15:
                score += 3.0
            if len(contours) < 8:
                score += 2.0

        # Stroke width variation — script has high variation
        dist = cv2.distanceTransform(self.binary, cv2.DIST_L2, 5)
        nonzero_dist = dist[dist > 0]
        if len(nonzero_dist) > 0:
            stroke_cv = np.std(nonzero_dist) / (np.mean(nonzero_dist) + 1e-6)
            if stroke_cv > 0.5:
                score += 2.0
            if stroke_cv > 0.8:
                score += 1.5

        # Horizontal projection irregularity
        h_proj = np.sum(self.binary, axis=1).astype(float)
        if len(h_proj) > 1:
            proj_cv = np.std(h_proj) / (np.mean(h_proj) + 1e-6)
            if proj_cv > 0.6:
                score += 1.5

        # Diagonal features — measure edge orientation
        sobelx = cv2.Sobel(self.gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(self.gray, cv2.CV_64F, 0, 1, ksize=3)
        angles = np.arctan2(np.abs(sobely), np.abs(sobelx) + 1e-6)
        diagonal_ratio = np.mean(
            (angles > np.pi/6) & (angles < np.pi/3)
        )
        if diagonal_ratio > 0.35:
            score += 1.5

        return score

    def _score_serif(self) -> float:
        """
        Serif fonts have:
        - Small horizontal strokes at ends of vertical strokes
        - High horizontal projection regularity
        - Moderate stroke width variation (thick/thin)
        - Strong vertical and horizontal edge presence
        """
        score = 0.0

        # Look for small horizontal strokes at top/bottom
        # of character region (serif indicators)
        h_proj = np.sum(self.binary, axis=0).astype(float)
        v_proj = np.sum(self.binary, axis=1).astype(float)

        if len(h_proj) > 0 and np.mean(h_proj) > 0:
            # Serifs create peaks at regular intervals
            try:
                from scipy.signal import find_peaks
                peaks, _ = find_peaks(h_proj, height=np.mean(h_proj)*0.3)
                if len(peaks) > 4:
                    score += 2.0
            except Exception:
                pass

        # Moderate stroke variation
        dist = cv2.distanceTransform(self.binary, cv2.DIST_L2, 5)
        nonzero = dist[dist > 0]
        if len(nonzero) > 0:
            cv_val = np.std(nonzero) / (np.mean(nonzero) + 1e-6)
            if 0.25 < cv_val < 0.55:
                score += 2.0

        # Strong vertical edges (straight vertical strokes)
        sobelx = cv2.Sobel(self.gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(self.gray, cv2.CV_64F, 0, 1, ksize=3)
        v_edge_strength = np.mean(np.abs(sobelx))
        h_edge_strength = np.mean(np.abs(sobely))
        if v_edge_strength > h_edge_strength * 1.2:
            score += 1.5

        return score

    def _score_sans(self) -> float:
        """
        Sans-serif fonts have:
        - Uniform stroke width throughout
        - Clean horizontal/vertical edges
        - Regular horizontal projection
        - Low stroke width variation
        """
        score = 0.0

        dist = cv2.distanceTransform(self.binary, cv2.DIST_L2, 5)
        nonzero = dist[dist > 0]
        if len(nonzero) > 0:
            cv_val = np.std(nonzero) / (np.mean(nonzero) + 1e-6)
            # Very uniform stroke = low coefficient of variation
            if cv_val < 0.25:
                score += 3.0
            elif cv_val < 0.35:
                score += 1.5

        # Regular horizontal projection = evenly spaced letters
        h_proj = np.sum(self.binary, axis=1).astype(float)
        if len(h_proj) > 1 and np.mean(h_proj) > 0:
            regularity = 1.0 - (
                np.std(h_proj) / (np.mean(h_proj) + 1e-6)
            )
            if regularity > 0.5:
                score += 2.0

        # Many separate character contours (not connected)
        contours, _ = cv2.findContours(
            self.binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if len(contours) >= 4:
            score += 1.5

        return score

    def _score_mono(self) -> float:
        """
        Monospace fonts have:
        - Very regular character spacing (equal width columns)
        - Uniform vertical projection
        """
        score = 0.0

        v_proj = np.sum(self.binary, axis=0).astype(float)
        if len(v_proj) > 1 and np.mean(v_proj) > 0:
            spacing_cv = np.std(v_proj) / (np.mean(v_proj) + 1e-6)
            if spacing_cv < 0.4:
                score += 3.0

        return score

    def _score_display(self) -> float:
        """
        Display/decorative fonts have:
        - Very high stroke width variation
        - Complex contour shapes
        - High pixel density variation
        """
        score = 0.0

        dist = cv2.distanceTransform(self.binary, cv2.DIST_L2, 5)
        nonzero = dist[dist > 0]
        if len(nonzero) > 0:
            cv_val = np.std(nonzero) / (np.mean(nonzero) + 1e-6)
            if cv_val > 1.0:
                score += 2.0

        contours, _ = cv2.findContours(
            self.binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
        )
        if len(contours) > 15:
            score += 1.5

        return score
