package internal

import "math/rand"

// Transform adds dummy enrichment fields
func Transform(raw map[string]interface{}) map[string]interface{} {
	transformed := make(map[string]interface{})
	for k, v := range raw {
		transformed[k] = v
	}

	// Add dummy enrichment
	transformed["country"] = "DummyCountry"
	transformed["region"] = "DummyRegion"
	transformed["city"] = "DummyCity"
	transformed["timezone"] = "UTC+0"
	transformed["population_density"] = rand.Float64() * 1000

	return transformed
}
