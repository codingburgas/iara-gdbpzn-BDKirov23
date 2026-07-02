from geopy.distance import distance


class NavigationService:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        return distance((lat1, lon1), (lat2, lon2)).kilometers

    @staticmethod
    def get_navigation_url(lat, lon):
        return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"

    @staticmethod
    def get_teams_in_radius(teams_with_coords, target_lat, target_lon, radius_km):
        nearby = []
        for team_id, lat, lon in teams_with_coords:
            if lat and lon:
                dist = NavigationService.calculate_distance(lat, lon, target_lat, target_lon)
                if dist <= radius_km:
                    nearby.append({"team_id": team_id, "distance_km": round(dist, 2)})
        return sorted(nearby, key=lambda x: x["distance_km"])
