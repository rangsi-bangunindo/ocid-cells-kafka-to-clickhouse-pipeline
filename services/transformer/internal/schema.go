package internal

import (
	"os"

	"github.com/hamba/avro/v2"
)

var (
	CellRawSchema         avro.Schema
	CellTransformedSchema avro.Schema
)

func LoadSchema() error {
	// Load raw schema
	rawData, err := os.ReadFile("/app/common/schema/cell_raw.avsc")
	if err != nil {
		return err
	}
	rawSchema, err := avro.Parse(string(rawData))
	if err != nil {
		return err
	}
	CellRawSchema = rawSchema

	// Load transformed schema
	transData, err := os.ReadFile("/app/common/schema/cell_transformed.avsc")
	if err != nil {
		return err
	}
	transSchema, err := avro.Parse(string(transData))
	if err != nil {
		return err
	}
	CellTransformedSchema = transSchema

	return nil
}
