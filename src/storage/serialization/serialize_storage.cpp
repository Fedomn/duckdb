//===----------------------------------------------------------------------===//
// This file is automatically generated by scripts/generate_serialization.py
// Do not edit this file manually, your changes will be overwritten
//===----------------------------------------------------------------------===//

#include "duckdb/common/serializer/serializer.hpp"
#include "duckdb/common/serializer/deserializer.hpp"
#include "duckdb/storage/block.hpp"
#include "duckdb/storage/block.hpp"
#include "duckdb/storage/data_pointer.hpp"
#include "duckdb/storage/statistics/distinct_statistics.hpp"

namespace duckdb {

void BlockPointer::FormatSerialize(FormatSerializer &serializer) const {
	serializer.WriteProperty(100, "block_id", block_id);
	serializer.WriteProperty(101, "offset", offset);
}

BlockPointer BlockPointer::FormatDeserialize(FormatDeserializer &deserializer) {
	auto block_id = deserializer.ReadProperty<block_id_t>(100, "block_id");
	auto offset = deserializer.ReadProperty<uint32_t>(101, "offset");
	BlockPointer result(block_id, offset);
	return result;
}

void DataPointer::FormatSerialize(FormatSerializer &serializer) const {
	serializer.WriteProperty(100, "row_start", row_start);
	serializer.WriteProperty(101, "tuple_count", tuple_count);
	serializer.WriteProperty(102, "block_pointer", block_pointer);
	serializer.WriteProperty(103, "compression_type", compression_type);
	serializer.WriteProperty(104, "statistics", statistics);
}

DataPointer DataPointer::FormatDeserialize(FormatDeserializer &deserializer) {
	auto row_start = deserializer.ReadProperty<uint64_t>(100, "row_start");
	auto tuple_count = deserializer.ReadProperty<uint64_t>(101, "tuple_count");
	auto block_pointer = deserializer.ReadProperty<BlockPointer>(102, "block_pointer");
	auto compression_type = deserializer.ReadProperty<CompressionType>(103, "compression_type");
	auto statistics = deserializer.ReadProperty<BaseStatistics>(104, "statistics");
	DataPointer result(std::move(statistics));
	result.row_start = row_start;
	result.tuple_count = tuple_count;
	result.block_pointer = block_pointer;
	result.compression_type = compression_type;
	return result;
}

void DistinctStatistics::FormatSerialize(FormatSerializer &serializer) const {
	serializer.WriteProperty(100, "sample_count", sample_count);
	serializer.WriteProperty(101, "total_count", total_count);
	serializer.WriteProperty(102, "log", log);
}

unique_ptr<DistinctStatistics> DistinctStatistics::FormatDeserialize(FormatDeserializer &deserializer) {
	auto sample_count = deserializer.ReadProperty<idx_t>(100, "sample_count");
	auto total_count = deserializer.ReadProperty<idx_t>(101, "total_count");
	auto log = deserializer.ReadProperty<unique_ptr<HyperLogLog>>(102, "log");
	auto result = duckdb::unique_ptr<DistinctStatistics>(new DistinctStatistics(std::move(log), sample_count, total_count));
	return result;
}

void MetaBlockPointer::FormatSerialize(FormatSerializer &serializer) const {
	serializer.WriteProperty(100, "block_pointer", block_pointer);
	serializer.WriteProperty(101, "offset", offset);
}

MetaBlockPointer MetaBlockPointer::FormatDeserialize(FormatDeserializer &deserializer) {
	auto block_pointer = deserializer.ReadProperty<idx_t>(100, "block_pointer");
	auto offset = deserializer.ReadProperty<uint32_t>(101, "offset");
	MetaBlockPointer result(block_pointer, offset);
	return result;
}

} // namespace duckdb
