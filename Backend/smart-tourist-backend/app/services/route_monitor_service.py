"""Route monitoring service for deviation detection."""

from math import cos, radians, sqrt
from threading import RLock
from typing import Dict, List, Optional, Tuple

from app.ml.feature_engineering import haversine_distance_m

Coordinate = Tuple[float, float]


class RouteMonitorService:
    """In-memory planned route store with deviation checks."""

    def __init__(self) -> None:
        self._routes: Dict[str, List[Coordinate]] = {}
        self._lock = RLock()

    def set_planned_route(self, tourist_id: str, coordinates: List[Coordinate]) -> None:
        if len(coordinates) < 2:
            raise ValueError("Route must include at least two coordinates")
        with self._lock:
            self._routes[str(tourist_id)] = coordinates

    def get_planned_route(self, tourist_id: str) -> List[Coordinate]:
        with self._lock:
            return list(self._routes.get(str(tourist_id), []))

    def clear_planned_route(self, tourist_id: str) -> None:
        with self._lock:
            self._routes.pop(str(tourist_id), None)

    def check_route_deviation(
        self,
        tourist_id: str,
        latitude: float,
        longitude: float,
        threshold_meters: float = 100.0,
    ) -> Optional[Dict[str, float]]:
        route = self.get_planned_route(tourist_id)
        if len(route) < 2:
            return None

        current = (latitude, longitude)
        min_distance = min(
            self._distance_to_segment_m(current, route[idx], route[idx + 1])
            for idx in range(len(route) - 1)
        )

        if min_distance <= threshold_meters:
            return None

        return {
            "deviation_meters": float(min_distance),
            "threshold_meters": float(threshold_meters),
        }

    @staticmethod
    def _distance_to_segment_m(point: Coordinate, seg_start: Coordinate, seg_end: Coordinate) -> float:
        """Approximate distance from point to line segment in meters."""
        lat1, lon1 = seg_start
        lat2, lon2 = seg_end
        latp, lonp = point

        # Convert degrees to local planar meters around segment start.
        lat_scale = 111320.0
        lon_scale = 111320.0 * max(0.1, cos(radians(lat1)))

        ax, ay = 0.0, 0.0
        bx, by = (lat2 - lat1) * lat_scale, (lon2 - lon1) * lon_scale
        px, py = (latp - lat1) * lat_scale, (lonp - lon1) * lon_scale

        abx = bx - ax
        aby = by - ay
        apx = px - ax
        apy = py - ay
        ab_len_sq = abx * abx + aby * aby

        if ab_len_sq == 0:
            return haversine_distance_m(latp, lonp, lat1, lon1)

        t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab_len_sq))
        proj_x = ax + t * abx
        proj_y = ay + t * aby

        dx = px - proj_x
        dy = py - proj_y
        return sqrt(dx * dx + dy * dy)


route_monitor_service = RouteMonitorService()
