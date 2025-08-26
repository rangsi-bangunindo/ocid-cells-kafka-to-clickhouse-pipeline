package internal

type CellTowerRaw struct {
	Radio         string  `json:"radio"`
	Mcc           int     `json:"mcc"`
	Net           int     `json:"net"`
	Area          int     `json:"area"`
	Cell          int     `json:"cell"`
	Unit          int     `json:"unit"`
	Lon           float64 `json:"lon"`
	Lat           float64 `json:"lat"`
	Range         int     `json:"range"`
	Samples       int     `json:"samples"`
	Changeable    int     `json:"changeable"`
	Created       int64   `json:"created"`
	Updated       int64   `json:"updated"`
	AverageSignal int     `json:"averageSignal"`
}

type CellTowerTransformed struct {
	CellTowerRaw
	Country           *string  `json:"country,omitempty"`
	Region            *string  `json:"region,omitempty"`
	City              *string  `json:"city,omitempty"`
	Timezone          *string  `json:"timezone,omitempty"`
	PopulationDensity *float64 `json:"population_density,omitempty"`
}
