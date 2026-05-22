import math

def to_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0

def haversine(lat1, lon1, lat2, lon2):
    lat1 = to_float(lat1)
    lon1 = to_float(lon1)
    lat2 = to_float(lat2)
    lon2 = to_float(lon2)

    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(dlambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest(user_lat, user_lon, authorities):
    user_lat = to_float(user_lat)
    user_lon = to_float(user_lon)

    nearest = None
    min_dist = float('inf')

    for auth in authorities:
        auth_lat = to_float(auth.get('lat'))
        auth_lon = to_float(auth.get('lon'))

        dist = haversine(user_lat, user_lon, auth_lat, auth_lon)

        if dist < min_dist:
            min_dist = dist
            nearest = auth

    return nearest
