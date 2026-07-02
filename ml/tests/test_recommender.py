from ml.recommender import haversine_km, recommend_redistribution


def test_haversine_km_zero_distance():
    assert haversine_km(21.6, 83.4, 21.6, 83.4) == 0.0


def test_haversine_km_known_pair():
    # Delhi to Mumbai is roughly 1150-1170 km as the crow flies
    distance = haversine_km(28.6139, 77.2090, 19.0760, 72.8777)
    assert 1100 <= distance <= 1200


def test_recommend_redistribution_matches_deficit_to_nearest_surplus():
    centre_states = [
        # deficit: well below its 14-day threshold
        {"centre_id": "DEFICIT", "lat": 21.60, "lng": 83.40, "units_in_stock": 5, "avg_daily_consumption": 5, "reorder_threshold_days": 14},
        # surplus, close by
        {"centre_id": "SURPLUS_NEAR", "lat": 21.61, "lng": 83.41, "units_in_stock": 500, "avg_daily_consumption": 5, "reorder_threshold_days": 14},
        # surplus, far away
        {"centre_id": "SURPLUS_FAR", "lat": 25.00, "lng": 88.00, "units_in_stock": 500, "avg_daily_consumption": 5, "reorder_threshold_days": 14},
    ]
    recs = recommend_redistribution("M01", centre_states)

    assert len(recs) == 1
    rec = recs[0]
    assert rec["to_centre_id"] == "DEFICIT"
    assert rec["from_centre_id"] == "SURPLUS_NEAR"  # nearer surplus chosen over farther one
    assert rec["suggested_units"] > 0
    assert rec["urgency_score"] > 50


def test_recommend_redistribution_no_surplus_means_no_recommendations():
    centre_states = [
        {"centre_id": "DEFICIT", "lat": 21.60, "lng": 83.40, "units_in_stock": 5, "avg_daily_consumption": 5, "reorder_threshold_days": 14},
        {"centre_id": "ALSO_LOW", "lat": 21.61, "lng": 83.41, "units_in_stock": 8, "avg_daily_consumption": 5, "reorder_threshold_days": 14},
    ]
    recs = recommend_redistribution("M01", centre_states)
    assert recs == []


def test_recommend_redistribution_ranks_most_urgent_first():
    centre_states = [
        {"centre_id": "URGENT", "lat": 21.60, "lng": 83.40, "units_in_stock": 1, "avg_daily_consumption": 5, "reorder_threshold_days": 14},
        {"centre_id": "MILD", "lat": 21.62, "lng": 83.42, "units_in_stock": 40, "avg_daily_consumption": 5, "reorder_threshold_days": 14},
        {"centre_id": "SURPLUS", "lat": 21.61, "lng": 83.41, "units_in_stock": 1000, "avg_daily_consumption": 5, "reorder_threshold_days": 14},
    ]
    recs = recommend_redistribution("M01", centre_states)
    assert recs[0]["to_centre_id"] == "URGENT"
