from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class _AndExpression(_message.Message):
    __slots__ = ["first_expression", "second_expression"]
    FIRST_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    SECOND_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    first_expression: _FilterExpression
    second_expression: _FilterExpression
    def __init__(self, first_expression: _Optional[_Union[_FilterExpression, _Mapping]] = ..., second_expression: _Optional[_Union[_FilterExpression, _Mapping]] = ...) -> None: ...

class _CountItemsRequest(_message.Message):
    __slots__ = ["all", "index_name"]
    class All(_message.Message):
        __slots__ = []
        def __init__(self) -> None: ...
    ALL_FIELD_NUMBER: _ClassVar[int]
    INDEX_NAME_FIELD_NUMBER: _ClassVar[int]
    all: _CountItemsRequest.All
    index_name: str
    def __init__(self, index_name: _Optional[str] = ..., all: _Optional[_Union[_CountItemsRequest.All, _Mapping]] = ...) -> None: ...

class _CountItemsResponse(_message.Message):
    __slots__ = ["item_count"]
    ITEM_COUNT_FIELD_NUMBER: _ClassVar[int]
    item_count: int
    def __init__(self, item_count: _Optional[int] = ...) -> None: ...

class _DeleteItemBatchRequest(_message.Message):
    __slots__ = ["filter", "ids", "index_name"]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    INDEX_NAME_FIELD_NUMBER: _ClassVar[int]
    filter: _FilterExpression
    ids: _containers.RepeatedScalarFieldContainer[str]
    index_name: str
    def __init__(self, index_name: _Optional[str] = ..., ids: _Optional[_Iterable[str]] = ..., filter: _Optional[_Union[_FilterExpression, _Mapping]] = ...) -> None: ...

class _DeleteItemBatchResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class _EqualsExpression(_message.Message):
    __slots__ = ["boolean_value", "field", "float_value", "integer_value", "string_value"]
    BOOLEAN_VALUE_FIELD_NUMBER: _ClassVar[int]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    boolean_value: bool
    field: str
    float_value: float
    integer_value: int
    string_value: str
    def __init__(self, field: _Optional[str] = ..., string_value: _Optional[str] = ..., integer_value: _Optional[int] = ..., float_value: _Optional[float] = ..., boolean_value: bool = ...) -> None: ...

class _FilterExpression(_message.Message):
    __slots__ = ["and_expression", "equals_expression", "greater_than_expression", "greater_than_or_equal_expression", "id_in_set_expression", "less_than_expression", "less_than_or_equal_expression", "list_contains_expression", "not_expression", "or_expression"]
    AND_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    EQUALS_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    GREATER_THAN_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    GREATER_THAN_OR_EQUAL_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    ID_IN_SET_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    LESS_THAN_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    LESS_THAN_OR_EQUAL_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    LIST_CONTAINS_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    NOT_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    OR_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    and_expression: _AndExpression
    equals_expression: _EqualsExpression
    greater_than_expression: _GreaterThanExpression
    greater_than_or_equal_expression: _GreaterThanOrEqualExpression
    id_in_set_expression: _IdInSetExpression
    less_than_expression: _LessThanExpression
    less_than_or_equal_expression: _LessThanOrEqualExpression
    list_contains_expression: _ListContainsExpression
    not_expression: _NotExpression
    or_expression: _OrExpression
    def __init__(self, equals_expression: _Optional[_Union[_EqualsExpression, _Mapping]] = ..., and_expression: _Optional[_Union[_AndExpression, _Mapping]] = ..., or_expression: _Optional[_Union[_OrExpression, _Mapping]] = ..., not_expression: _Optional[_Union[_NotExpression, _Mapping]] = ..., greater_than_expression: _Optional[_Union[_GreaterThanExpression, _Mapping]] = ..., greater_than_or_equal_expression: _Optional[_Union[_GreaterThanOrEqualExpression, _Mapping]] = ..., less_than_expression: _Optional[_Union[_LessThanExpression, _Mapping]] = ..., less_than_or_equal_expression: _Optional[_Union[_LessThanOrEqualExpression, _Mapping]] = ..., list_contains_expression: _Optional[_Union[_ListContainsExpression, _Mapping]] = ..., id_in_set_expression: _Optional[_Union[_IdInSetExpression, _Mapping]] = ...) -> None: ...

class _GetItemBatchRequest(_message.Message):
    __slots__ = ["filter", "ids", "index_name", "metadata_fields"]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    INDEX_NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELDS_FIELD_NUMBER: _ClassVar[int]
    filter: _FilterExpression
    ids: _containers.RepeatedScalarFieldContainer[str]
    index_name: str
    metadata_fields: _MetadataRequest
    def __init__(self, index_name: _Optional[str] = ..., ids: _Optional[_Iterable[str]] = ..., metadata_fields: _Optional[_Union[_MetadataRequest, _Mapping]] = ..., filter: _Optional[_Union[_FilterExpression, _Mapping]] = ...) -> None: ...

class _GetItemBatchResponse(_message.Message):
    __slots__ = ["item_response"]
    ITEM_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    item_response: _containers.RepeatedCompositeFieldContainer[_ItemResponse]
    def __init__(self, item_response: _Optional[_Iterable[_Union[_ItemResponse, _Mapping]]] = ...) -> None: ...

class _GetItemMetadataBatchRequest(_message.Message):
    __slots__ = ["filter", "ids", "index_name", "metadata_fields"]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    INDEX_NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELDS_FIELD_NUMBER: _ClassVar[int]
    filter: _FilterExpression
    ids: _containers.RepeatedScalarFieldContainer[str]
    index_name: str
    metadata_fields: _MetadataRequest
    def __init__(self, index_name: _Optional[str] = ..., ids: _Optional[_Iterable[str]] = ..., metadata_fields: _Optional[_Union[_MetadataRequest, _Mapping]] = ..., filter: _Optional[_Union[_FilterExpression, _Mapping]] = ...) -> None: ...

class _GetItemMetadataBatchResponse(_message.Message):
    __slots__ = ["item_metadata_response"]
    ITEM_METADATA_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    item_metadata_response: _containers.RepeatedCompositeFieldContainer[_ItemMetadataResponse]
    def __init__(self, item_metadata_response: _Optional[_Iterable[_Union[_ItemMetadataResponse, _Mapping]]] = ...) -> None: ...

class _GreaterThanExpression(_message.Message):
    __slots__ = ["field", "float_value", "integer_value"]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    field: str
    float_value: float
    integer_value: int
    def __init__(self, field: _Optional[str] = ..., integer_value: _Optional[int] = ..., float_value: _Optional[float] = ...) -> None: ...

class _GreaterThanOrEqualExpression(_message.Message):
    __slots__ = ["field", "float_value", "integer_value"]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    field: str
    float_value: float
    integer_value: int
    def __init__(self, field: _Optional[str] = ..., integer_value: _Optional[int] = ..., float_value: _Optional[float] = ...) -> None: ...

class _IdInSetExpression(_message.Message):
    __slots__ = ["ids"]
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ids: _Optional[_Iterable[str]] = ...) -> None: ...

class _Item(_message.Message):
    __slots__ = ["id", "metadata", "vector"]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    metadata: _containers.RepeatedCompositeFieldContainer[_Metadata]
    vector: _Vector
    def __init__(self, id: _Optional[str] = ..., vector: _Optional[_Union[_Vector, _Mapping]] = ..., metadata: _Optional[_Iterable[_Union[_Metadata, _Mapping]]] = ...) -> None: ...

class _ItemMetadataResponse(_message.Message):
    __slots__ = ["hit", "id", "metadata", "miss"]
    class _Hit(_message.Message):
        __slots__ = ["id", "metadata"]
        ID_FIELD_NUMBER: _ClassVar[int]
        METADATA_FIELD_NUMBER: _ClassVar[int]
        id: str
        metadata: _containers.RepeatedCompositeFieldContainer[_Metadata]
        def __init__(self, id: _Optional[str] = ..., metadata: _Optional[_Iterable[_Union[_Metadata, _Mapping]]] = ...) -> None: ...
    class _Miss(_message.Message):
        __slots__ = []
        def __init__(self) -> None: ...
    HIT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    MISS_FIELD_NUMBER: _ClassVar[int]
    hit: _ItemMetadataResponse._Hit
    id: str
    metadata: _containers.RepeatedCompositeFieldContainer[_Metadata]
    miss: _ItemMetadataResponse._Miss
    def __init__(self, miss: _Optional[_Union[_ItemMetadataResponse._Miss, _Mapping]] = ..., hit: _Optional[_Union[_ItemMetadataResponse._Hit, _Mapping]] = ..., id: _Optional[str] = ..., metadata: _Optional[_Iterable[_Union[_Metadata, _Mapping]]] = ...) -> None: ...

class _ItemResponse(_message.Message):
    __slots__ = ["hit", "id", "metadata", "miss", "vector"]
    class _Hit(_message.Message):
        __slots__ = ["id", "metadata", "vector"]
        ID_FIELD_NUMBER: _ClassVar[int]
        METADATA_FIELD_NUMBER: _ClassVar[int]
        VECTOR_FIELD_NUMBER: _ClassVar[int]
        id: str
        metadata: _containers.RepeatedCompositeFieldContainer[_Metadata]
        vector: _Vector
        def __init__(self, id: _Optional[str] = ..., vector: _Optional[_Union[_Vector, _Mapping]] = ..., metadata: _Optional[_Iterable[_Union[_Metadata, _Mapping]]] = ...) -> None: ...
    class _Miss(_message.Message):
        __slots__ = []
        def __init__(self) -> None: ...
    HIT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    MISS_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    hit: _ItemResponse._Hit
    id: str
    metadata: _containers.RepeatedCompositeFieldContainer[_Metadata]
    miss: _ItemResponse._Miss
    vector: _Vector
    def __init__(self, miss: _Optional[_Union[_ItemResponse._Miss, _Mapping]] = ..., hit: _Optional[_Union[_ItemResponse._Hit, _Mapping]] = ..., id: _Optional[str] = ..., vector: _Optional[_Union[_Vector, _Mapping]] = ..., metadata: _Optional[_Iterable[_Union[_Metadata, _Mapping]]] = ...) -> None: ...

class _LessThanExpression(_message.Message):
    __slots__ = ["field", "float_value", "integer_value"]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    field: str
    float_value: float
    integer_value: int
    def __init__(self, field: _Optional[str] = ..., integer_value: _Optional[int] = ..., float_value: _Optional[float] = ...) -> None: ...

class _LessThanOrEqualExpression(_message.Message):
    __slots__ = ["field", "float_value", "integer_value"]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    field: str
    float_value: float
    integer_value: int
    def __init__(self, field: _Optional[str] = ..., integer_value: _Optional[int] = ..., float_value: _Optional[float] = ...) -> None: ...

class _ListContainsExpression(_message.Message):
    __slots__ = ["field", "string_value"]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    field: str
    string_value: str
    def __init__(self, field: _Optional[str] = ..., string_value: _Optional[str] = ...) -> None: ...

class _Metadata(_message.Message):
    __slots__ = ["boolean_value", "double_value", "field", "integer_value", "list_of_strings_value", "string_value"]
    class _ListOfStrings(_message.Message):
        __slots__ = ["values"]
        VALUES_FIELD_NUMBER: _ClassVar[int]
        values: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...
    BOOLEAN_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    LIST_OF_STRINGS_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    boolean_value: bool
    double_value: float
    field: str
    integer_value: int
    list_of_strings_value: _Metadata._ListOfStrings
    string_value: str
    def __init__(self, field: _Optional[str] = ..., string_value: _Optional[str] = ..., integer_value: _Optional[int] = ..., double_value: _Optional[float] = ..., boolean_value: bool = ..., list_of_strings_value: _Optional[_Union[_Metadata._ListOfStrings, _Mapping]] = ...) -> None: ...

class _MetadataRequest(_message.Message):
    __slots__ = ["all", "some"]
    class All(_message.Message):
        __slots__ = []
        def __init__(self) -> None: ...
    class Some(_message.Message):
        __slots__ = ["fields"]
        FIELDS_FIELD_NUMBER: _ClassVar[int]
        fields: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, fields: _Optional[_Iterable[str]] = ...) -> None: ...
    ALL_FIELD_NUMBER: _ClassVar[int]
    SOME_FIELD_NUMBER: _ClassVar[int]
    all: _MetadataRequest.All
    some: _MetadataRequest.Some
    def __init__(self, some: _Optional[_Union[_MetadataRequest.Some, _Mapping]] = ..., all: _Optional[_Union[_MetadataRequest.All, _Mapping]] = ...) -> None: ...

class _NoScoreThreshold(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class _NotExpression(_message.Message):
    __slots__ = ["expression_to_negate"]
    EXPRESSION_TO_NEGATE_FIELD_NUMBER: _ClassVar[int]
    expression_to_negate: _FilterExpression
    def __init__(self, expression_to_negate: _Optional[_Union[_FilterExpression, _Mapping]] = ...) -> None: ...

class _OrExpression(_message.Message):
    __slots__ = ["first_expression", "second_expression"]
    FIRST_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    SECOND_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    first_expression: _FilterExpression
    second_expression: _FilterExpression
    def __init__(self, first_expression: _Optional[_Union[_FilterExpression, _Mapping]] = ..., second_expression: _Optional[_Union[_FilterExpression, _Mapping]] = ...) -> None: ...

class _SearchAndFetchVectorsHit(_message.Message):
    __slots__ = ["id", "metadata", "score", "vector"]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    metadata: _containers.RepeatedCompositeFieldContainer[_Metadata]
    score: float
    vector: _Vector
    def __init__(self, id: _Optional[str] = ..., score: _Optional[float] = ..., metadata: _Optional[_Iterable[_Union[_Metadata, _Mapping]]] = ..., vector: _Optional[_Union[_Vector, _Mapping]] = ...) -> None: ...

class _SearchAndFetchVectorsRequest(_message.Message):
    __slots__ = ["filter", "index_name", "metadata_fields", "no_score_threshold", "query_vector", "score_threshold", "top_k"]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    INDEX_NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELDS_FIELD_NUMBER: _ClassVar[int]
    NO_SCORE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    QUERY_VECTOR_FIELD_NUMBER: _ClassVar[int]
    SCORE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    filter: _FilterExpression
    index_name: str
    metadata_fields: _MetadataRequest
    no_score_threshold: _NoScoreThreshold
    query_vector: _Vector
    score_threshold: float
    top_k: int
    def __init__(self, index_name: _Optional[str] = ..., top_k: _Optional[int] = ..., query_vector: _Optional[_Union[_Vector, _Mapping]] = ..., metadata_fields: _Optional[_Union[_MetadataRequest, _Mapping]] = ..., score_threshold: _Optional[float] = ..., no_score_threshold: _Optional[_Union[_NoScoreThreshold, _Mapping]] = ..., filter: _Optional[_Union[_FilterExpression, _Mapping]] = ...) -> None: ...

class _SearchAndFetchVectorsResponse(_message.Message):
    __slots__ = ["hits"]
    HITS_FIELD_NUMBER: _ClassVar[int]
    hits: _containers.RepeatedCompositeFieldContainer[_SearchAndFetchVectorsHit]
    def __init__(self, hits: _Optional[_Iterable[_Union[_SearchAndFetchVectorsHit, _Mapping]]] = ...) -> None: ...

class _SearchHit(_message.Message):
    __slots__ = ["id", "metadata", "score"]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    id: str
    metadata: _containers.RepeatedCompositeFieldContainer[_Metadata]
    score: float
    def __init__(self, id: _Optional[str] = ..., score: _Optional[float] = ..., metadata: _Optional[_Iterable[_Union[_Metadata, _Mapping]]] = ...) -> None: ...

class _SearchRequest(_message.Message):
    __slots__ = ["filter", "index_name", "metadata_fields", "no_score_threshold", "query_vector", "score_threshold", "top_k"]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    INDEX_NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELDS_FIELD_NUMBER: _ClassVar[int]
    NO_SCORE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    QUERY_VECTOR_FIELD_NUMBER: _ClassVar[int]
    SCORE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    filter: _FilterExpression
    index_name: str
    metadata_fields: _MetadataRequest
    no_score_threshold: _NoScoreThreshold
    query_vector: _Vector
    score_threshold: float
    top_k: int
    def __init__(self, index_name: _Optional[str] = ..., top_k: _Optional[int] = ..., query_vector: _Optional[_Union[_Vector, _Mapping]] = ..., metadata_fields: _Optional[_Union[_MetadataRequest, _Mapping]] = ..., score_threshold: _Optional[float] = ..., no_score_threshold: _Optional[_Union[_NoScoreThreshold, _Mapping]] = ..., filter: _Optional[_Union[_FilterExpression, _Mapping]] = ...) -> None: ...

class _SearchResponse(_message.Message):
    __slots__ = ["hits"]
    HITS_FIELD_NUMBER: _ClassVar[int]
    hits: _containers.RepeatedCompositeFieldContainer[_SearchHit]
    def __init__(self, hits: _Optional[_Iterable[_Union[_SearchHit, _Mapping]]] = ...) -> None: ...

class _UpsertItemBatchRequest(_message.Message):
    __slots__ = ["index_name", "items"]
    INDEX_NAME_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    index_name: str
    items: _containers.RepeatedCompositeFieldContainer[_Item]
    def __init__(self, index_name: _Optional[str] = ..., items: _Optional[_Iterable[_Union[_Item, _Mapping]]] = ...) -> None: ...

class _UpsertItemBatchResponse(_message.Message):
    __slots__ = ["error_indices"]
    ERROR_INDICES_FIELD_NUMBER: _ClassVar[int]
    error_indices: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, error_indices: _Optional[_Iterable[int]] = ...) -> None: ...

class _Vector(_message.Message):
    __slots__ = ["elements"]
    ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    elements: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, elements: _Optional[_Iterable[float]] = ...) -> None: ...
