//===----------------------------------------------------------------------===//
//                         DuckDB
//
// duckdb/core_functions/lambda_functions.hpp
//
//
//===----------------------------------------------------------------------===//

// FIXME: more const, slimmer functions (there are some pretty massive parameters - structs?)

#pragma once

namespace duckdb {

enum class LambdaType : uint8_t {
	TRANSFORM = 1,
	FILTER = 2,
	REDUCE = 3,
};

struct ListLambdaBindData : public FunctionData {
	ListLambdaBindData(const LogicalType &return_type, unique_ptr<Expression> lambda_expr,
	                   const bool has_index = false);

	//! Return type of the scalar function
	LogicalType return_type;
	//! Lambda expression that the expression executor executes
	unique_ptr<Expression> lambda_expr;
	//! True, if list_transform has two lambda parameters (the second parameter is the index of the
	//! first parameter in the list)
	bool has_index;

public:
	bool Equals(const FunctionData &other_p) const override;
	unique_ptr<FunctionData> Copy() const override;

	//! Old (de)serialization functionality
	static void Serialize(FieldWriter &, const FunctionData *, const ScalarFunction &);
	static unique_ptr<FunctionData> Deserialize(PlanDeserializationState &, FieldReader &, ScalarFunction &);

	//! Serialize a lambda function's bind data
	static void FormatSerialize(FormatSerializer &serializer, const optional_ptr<FunctionData> bind_data_p,
	                            const ScalarFunction &function);
	//! Deserialize a lambda function's bind data
	static unique_ptr<FunctionData> FormatDeserialize(FormatDeserializer &deserializer, ScalarFunction &);
};

struct LambdaFunctions {

	// FIXME: still a pretty massive function
	// FIXME: more separation between different lambda functions (enum as parameter with lambda function type?)
	static void ExecuteLambda(DataChunk &args, ExpressionState &state, Vector &result, LambdaType lambda_type);

	//! Generic binding functionality of lambda functions
	static unique_ptr<FunctionData> ListLambdaBind(ClientContext &, ScalarFunction &bound_function,
	                                               vector<unique_ptr<Expression>> &arguments,
	                                               const idx_t parameter_count, const bool has_index = false);
};

} // namespace duckdb
