---
annotations_creators:
- derived
language:
- eng
license: mit
multilinguality: monolingual
source_datasets:
- KaLM-Embedding/LMEB
task_categories:
- text-retrieval
task_ids:
- multiple-choice-qa
dataset_info:
- config_name: default_claude_long__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 504470
    num_examples: 196
  download_size: 303686
  dataset_size: 504470
- config_name: default_claude_long__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 14313
    num_examples: 347
  download_size: 3537
  dataset_size: 14313
- config_name: default_claude_long__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 17257
    num_examples: 98
  download_size: 4823
  dataset_size: 17257
- config_name: default_claude_long__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 504470
    num_examples: 196
  download_size: 303686
  dataset_size: 504470
- config_name: default_claude_long__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 16342
    num_examples: 393
  download_size: 3672
  dataset_size: 16342
- config_name: default_claude_long__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 20887
    num_examples: 122
  download_size: 5192
  dataset_size: 20887
- config_name: default_claude_long__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 504470
    num_examples: 196
  download_size: 303686
  dataset_size: 504470
- config_name: default_claude_long__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 201
    num_examples: 5
  download_size: 1796
  dataset_size: 201
- config_name: default_claude_long__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1284
    num_examples: 5
  download_size: 2627
  dataset_size: 1284
- config_name: default_claude_long__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 504470
    num_examples: 196
  download_size: 303686
  dataset_size: 504470
- config_name: default_claude_long__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 201
    num_examples: 5
  download_size: 1796
  dataset_size: 201
- config_name: default_claude_long__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 834
    num_examples: 5
  download_size: 2195
  dataset_size: 834
- config_name: default_claude_long__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 504470
    num_examples: 196
  download_size: 303686
  dataset_size: 504470
- config_name: default_claude_long__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 17091
    num_examples: 412
  download_size: 3835
  dataset_size: 17091
- config_name: default_claude_long__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 21096
    num_examples: 132
  download_size: 5305
  dataset_size: 21096
- config_name: default_claude_long__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 504470
    num_examples: 196
  download_size: 303686
  dataset_size: 504470
- config_name: default_claude_long__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 18732
    num_examples: 451
  download_size: 3962
  dataset_size: 18732
- config_name: default_claude_long__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 22918
    num_examples: 144
  download_size: 5651
  dataset_size: 22918
- config_name: default_claude_short__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 50971
    num_examples: 19
  download_size: 40491
  dataset_size: 50971
- config_name: default_claude_short__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 2985
    num_examples: 74
  download_size: 2178
  dataset_size: 2985
- config_name: default_claude_short__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 9388
    num_examples: 52
  download_size: 3707
  dataset_size: 9388
- config_name: default_claude_short__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 50971
    num_examples: 19
  download_size: 40491
  dataset_size: 50971
- config_name: default_claude_short__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 3879
    num_examples: 96
  download_size: 2290
  dataset_size: 3879
- config_name: default_claude_short__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 12142
    num_examples: 71
  download_size: 4032
  dataset_size: 12142
- config_name: default_claude_short__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 50971
    num_examples: 19
  download_size: 40491
  dataset_size: 50971
- config_name: default_claude_short__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 198
    num_examples: 5
  download_size: 1788
  dataset_size: 198
- config_name: default_claude_short__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1340
    num_examples: 5
  download_size: 2763
  dataset_size: 1340
- config_name: default_claude_short__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 50971
    num_examples: 19
  download_size: 40491
  dataset_size: 50971
- config_name: default_claude_short__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 198
    num_examples: 5
  download_size: 1788
  dataset_size: 198
- config_name: default_claude_short__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 890
    num_examples: 5
  download_size: 2303
  dataset_size: 890
- config_name: default_claude_short__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 50971
    num_examples: 19
  download_size: 40491
  dataset_size: 50971
- config_name: default_claude_short__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 3957
    num_examples: 98
  download_size: 2304
  dataset_size: 3957
- config_name: default_claude_short__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11362
    num_examples: 71
  download_size: 3768
  dataset_size: 11362
- config_name: default_claude_short__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 50971
    num_examples: 19
  download_size: 40491
  dataset_size: 50971
- config_name: default_claude_short__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 4037
    num_examples: 100
  download_size: 2308
  dataset_size: 4037
- config_name: default_claude_short__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11272
    num_examples: 72
  download_size: 3859
  dataset_size: 11272
- config_name: default_claude_very_long__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 5060788
    num_examples: 1967
  download_size: 3013570
  dataset_size: 5060788
- config_name: default_claude_very_long__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 35059
    num_examples: 827
  download_size: 6601
  dataset_size: 35059
- config_name: default_claude_very_long__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 16965
    num_examples: 95
  download_size: 4806
  dataset_size: 16965
- config_name: default_claude_very_long__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 5060788
    num_examples: 1967
  download_size: 3013570
  dataset_size: 5060788
- config_name: default_claude_very_long__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 34247
    num_examples: 804
  download_size: 6237
  dataset_size: 34247
- config_name: default_claude_very_long__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 20456
    num_examples: 120
  download_size: 5113
  dataset_size: 20456
- config_name: default_claude_very_long__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 5060788
    num_examples: 1967
  download_size: 3013570
  dataset_size: 5060788
- config_name: default_claude_very_long__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 204
    num_examples: 5
  download_size: 1803
  dataset_size: 204
- config_name: default_claude_very_long__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1305
    num_examples: 5
  download_size: 2679
  dataset_size: 1305
- config_name: default_claude_very_long__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 5060788
    num_examples: 1967
  download_size: 3013570
  dataset_size: 5060788
- config_name: default_claude_very_long__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 204
    num_examples: 5
  download_size: 1803
  dataset_size: 204
- config_name: default_claude_very_long__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 855
    num_examples: 5
  download_size: 2248
  dataset_size: 855
- config_name: default_claude_very_long__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 5060788
    num_examples: 1967
  download_size: 3013570
  dataset_size: 5060788
- config_name: default_claude_very_long__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 35025
    num_examples: 820
  download_size: 6265
  dataset_size: 35025
- config_name: default_claude_very_long__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 22019
    num_examples: 137
  download_size: 5465
  dataset_size: 22019
- config_name: default_claude_very_long__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 5060788
    num_examples: 1967
  download_size: 3013570
  dataset_size: 5060788
- config_name: default_claude_very_long__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 47858
    num_examples: 1116
  download_size: 7791
  dataset_size: 47858
- config_name: default_claude_very_long__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 27953
    num_examples: 171
  download_size: 6451
  dataset_size: 27953
- config_name: default_gpt4o_long__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 612365
    num_examples: 196
  download_size: 377753
  dataset_size: 612365
- config_name: default_gpt4o_long__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 14274
    num_examples: 346
  download_size: 3533
  dataset_size: 14274
- config_name: default_gpt4o_long__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 17252
    num_examples: 98
  download_size: 4800
  dataset_size: 17252
- config_name: default_gpt4o_long__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 612365
    num_examples: 196
  download_size: 377753
  dataset_size: 612365
- config_name: default_gpt4o_long__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 16085
    num_examples: 387
  download_size: 3640
  dataset_size: 16085
- config_name: default_gpt4o_long__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 20663
    num_examples: 121
  download_size: 5198
  dataset_size: 20663
- config_name: default_gpt4o_long__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 612365
    num_examples: 196
  download_size: 377753
  dataset_size: 612365
- config_name: default_gpt4o_long__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 201
    num_examples: 5
  download_size: 1797
  dataset_size: 201
- config_name: default_gpt4o_long__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1284
    num_examples: 5
  download_size: 2627
  dataset_size: 1284
- config_name: default_gpt4o_long__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 612365
    num_examples: 196
  download_size: 377753
  dataset_size: 612365
- config_name: default_gpt4o_long__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 201
    num_examples: 5
  download_size: 1797
  dataset_size: 201
- config_name: default_gpt4o_long__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 834
    num_examples: 5
  download_size: 2195
  dataset_size: 834
- config_name: default_gpt4o_long__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 612365
    num_examples: 196
  download_size: 377753
  dataset_size: 612365
- config_name: default_gpt4o_long__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 16837
    num_examples: 406
  download_size: 3824
  dataset_size: 16837
- config_name: default_gpt4o_long__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 21083
    num_examples: 132
  download_size: 5299
  dataset_size: 21083
- config_name: default_gpt4o_long__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 612365
    num_examples: 196
  download_size: 377753
  dataset_size: 612365
- config_name: default_gpt4o_long__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 18393
    num_examples: 443
  download_size: 3939
  dataset_size: 18393
- config_name: default_gpt4o_long__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 22728
    num_examples: 143
  download_size: 5592
  dataset_size: 22728
- config_name: default_gpt4o_short__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 67241
    num_examples: 20
  download_size: 52402
  dataset_size: 67241
- config_name: default_gpt4o_short__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 3068
    num_examples: 76
  download_size: 2182
  dataset_size: 3068
- config_name: default_gpt4o_short__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 9377
    num_examples: 52
  download_size: 3717
  dataset_size: 9377
- config_name: default_gpt4o_short__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 67241
    num_examples: 20
  download_size: 52402
  dataset_size: 67241
- config_name: default_gpt4o_short__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 4003
    num_examples: 99
  download_size: 2311
  dataset_size: 4003
- config_name: default_gpt4o_short__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 12143
    num_examples: 71
  download_size: 4055
  dataset_size: 12143
- config_name: default_gpt4o_short__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 67241
    num_examples: 20
  download_size: 52402
  dataset_size: 67241
- config_name: default_gpt4o_short__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 198
    num_examples: 5
  download_size: 1786
  dataset_size: 198
- config_name: default_gpt4o_short__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1340
    num_examples: 5
  download_size: 2763
  dataset_size: 1340
- config_name: default_gpt4o_short__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 67241
    num_examples: 20
  download_size: 52402
  dataset_size: 67241
- config_name: default_gpt4o_short__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 198
    num_examples: 5
  download_size: 1786
  dataset_size: 198
- config_name: default_gpt4o_short__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 890
    num_examples: 5
  download_size: 2303
  dataset_size: 890
- config_name: default_gpt4o_short__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 67241
    num_examples: 20
  download_size: 52402
  dataset_size: 67241
- config_name: default_gpt4o_short__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 4164
    num_examples: 103
  download_size: 2308
  dataset_size: 4164
- config_name: default_gpt4o_short__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11536
    num_examples: 72
  download_size: 3782
  dataset_size: 11536
- config_name: default_gpt4o_short__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 67241
    num_examples: 20
  download_size: 52402
  dataset_size: 67241
- config_name: default_gpt4o_short__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 4283
    num_examples: 106
  download_size: 2324
  dataset_size: 4283
- config_name: default_gpt4o_short__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11439
    num_examples: 73
  download_size: 3889
  dataset_size: 11439
- config_name: sci_fi_claude_long__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 493354
    num_examples: 200
  download_size: 276887
  dataset_size: 493354
- config_name: sci_fi_claude_long__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 13990
    num_examples: 339
  download_size: 3544
  dataset_size: 13990
- config_name: sci_fi_claude_long__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 18093
    num_examples: 99
  download_size: 5183
  dataset_size: 18093
- config_name: sci_fi_claude_long__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 493354
    num_examples: 200
  download_size: 276887
  dataset_size: 493354
- config_name: sci_fi_claude_long__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 16063
    num_examples: 387
  download_size: 3638
  dataset_size: 16063
- config_name: sci_fi_claude_long__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 19885
    num_examples: 115
  download_size: 5190
  dataset_size: 19885
- config_name: sci_fi_claude_long__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 493354
    num_examples: 200
  download_size: 276887
  dataset_size: 493354
- config_name: sci_fi_claude_long__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 203
    num_examples: 5
  download_size: 1797
  dataset_size: 203
- config_name: sci_fi_claude_long__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1357
    num_examples: 5
  download_size: 2769
  dataset_size: 1357
- config_name: sci_fi_claude_long__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 493354
    num_examples: 200
  download_size: 276887
  dataset_size: 493354
- config_name: sci_fi_claude_long__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 203
    num_examples: 5
  download_size: 1797
  dataset_size: 203
- config_name: sci_fi_claude_long__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 907
    num_examples: 5
  download_size: 2329
  dataset_size: 907
- config_name: sci_fi_claude_long__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 493354
    num_examples: 200
  download_size: 276887
  dataset_size: 493354
- config_name: sci_fi_claude_long__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 17651
    num_examples: 426
  download_size: 3819
  dataset_size: 17651
- config_name: sci_fi_claude_long__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 21031
    num_examples: 128
  download_size: 5390
  dataset_size: 21031
- config_name: sci_fi_claude_long__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 493354
    num_examples: 200
  download_size: 276887
  dataset_size: 493354
- config_name: sci_fi_claude_long__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 19068
    num_examples: 459
  download_size: 3932
  dataset_size: 19068
- config_name: sci_fi_claude_long__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 22118
    num_examples: 136
  download_size: 5828
  dataset_size: 22118
- config_name: sci_fi_claude_short__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 49406
    num_examples: 20
  download_size: 38735
  dataset_size: 49406
- config_name: sci_fi_claude_short__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 2580
    num_examples: 64
  download_size: 2134
  dataset_size: 2580
- config_name: sci_fi_claude_short__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 8858
    num_examples: 48
  download_size: 3693
  dataset_size: 8858
- config_name: sci_fi_claude_short__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 49406
    num_examples: 20
  download_size: 38735
  dataset_size: 49406
- config_name: sci_fi_claude_short__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 3804
    num_examples: 94
  download_size: 2290
  dataset_size: 3804
- config_name: sci_fi_claude_short__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11977
    num_examples: 71
  download_size: 3972
  dataset_size: 11977
- config_name: sci_fi_claude_short__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 49406
    num_examples: 20
  download_size: 38735
  dataset_size: 49406
- config_name: sci_fi_claude_short__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 198
    num_examples: 5
  download_size: 1786
  dataset_size: 198
- config_name: sci_fi_claude_short__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1360
    num_examples: 5
  download_size: 2799
  dataset_size: 1360
- config_name: sci_fi_claude_short__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 49406
    num_examples: 20
  download_size: 38735
  dataset_size: 49406
- config_name: sci_fi_claude_short__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 198
    num_examples: 5
  download_size: 1786
  dataset_size: 198
- config_name: sci_fi_claude_short__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 910
    num_examples: 5
  download_size: 2338
  dataset_size: 910
- config_name: sci_fi_claude_short__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 49406
    num_examples: 20
  download_size: 38735
  dataset_size: 49406
- config_name: sci_fi_claude_short__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 3956
    num_examples: 98
  download_size: 2305
  dataset_size: 3956
- config_name: sci_fi_claude_short__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11557
    num_examples: 72
  download_size: 3889
  dataset_size: 11557
- config_name: sci_fi_claude_short__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 49406
    num_examples: 20
  download_size: 38735
  dataset_size: 49406
- config_name: sci_fi_claude_short__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 3839
    num_examples: 95
  download_size: 2289
  dataset_size: 3839
- config_name: sci_fi_claude_short__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11157
    num_examples: 71
  download_size: 3894
  dataset_size: 11157
- config_name: world_news_claude_long__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 400073
    num_examples: 200
  download_size: 221574
  dataset_size: 400073
- config_name: world_news_claude_long__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 13334
    num_examples: 323
  download_size: 3531
  dataset_size: 13334
- config_name: world_news_claude_long__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 17154
    num_examples: 98
  download_size: 4887
  dataset_size: 17154
- config_name: world_news_claude_long__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 400073
    num_examples: 200
  download_size: 221574
  dataset_size: 400073
- config_name: world_news_claude_long__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 14839
    num_examples: 357
  download_size: 3706
  dataset_size: 14839
- config_name: world_news_claude_long__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 20998
    num_examples: 126
  download_size: 5237
  dataset_size: 20998
- config_name: world_news_claude_long__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 400073
    num_examples: 200
  download_size: 221574
  dataset_size: 400073
- config_name: world_news_claude_long__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 202
    num_examples: 5
  download_size: 1795
  dataset_size: 202
- config_name: world_news_claude_long__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1291
    num_examples: 5
  download_size: 2680
  dataset_size: 1291
- config_name: world_news_claude_long__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 400073
    num_examples: 200
  download_size: 221574
  dataset_size: 400073
- config_name: world_news_claude_long__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 202
    num_examples: 5
  download_size: 1795
  dataset_size: 202
- config_name: world_news_claude_long__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 841
    num_examples: 5
  download_size: 2210
  dataset_size: 841
- config_name: world_news_claude_long__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 400073
    num_examples: 200
  download_size: 221574
  dataset_size: 400073
- config_name: world_news_claude_long__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 16938
    num_examples: 408
  download_size: 3881
  dataset_size: 16938
- config_name: world_news_claude_long__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 22048
    num_examples: 138
  download_size: 5527
  dataset_size: 22048
- config_name: world_news_claude_long__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 400073
    num_examples: 200
  download_size: 221574
  dataset_size: 400073
- config_name: world_news_claude_long__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 18077
    num_examples: 434
  download_size: 3981
  dataset_size: 18077
- config_name: world_news_claude_long__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 22469
    num_examples: 145
  download_size: 5696
  dataset_size: 22469
- config_name: world_news_claude_short__Entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 40430
    num_examples: 20
  download_size: 32620
  dataset_size: 40430
- config_name: world_news_claude_short__Entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 2906
    num_examples: 72
  download_size: 2155
  dataset_size: 2906
- config_name: world_news_claude_short__Entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 8547
    num_examples: 49
  download_size: 3435
  dataset_size: 8547
- config_name: world_news_claude_short__Event_contents-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 40430
    num_examples: 20
  download_size: 32620
  dataset_size: 40430
- config_name: world_news_claude_short__Event_contents-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 4050
    num_examples: 100
  download_size: 2302
  dataset_size: 4050
- config_name: world_news_claude_short__Event_contents-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11694
    num_examples: 70
  download_size: 3857
  dataset_size: 11694
- config_name: world_news_claude_short__Full_event_details-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 40430
    num_examples: 20
  download_size: 32620
  dataset_size: 40430
- config_name: world_news_claude_short__Full_event_details-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 198
    num_examples: 5
  download_size: 1790
  dataset_size: 198
- config_name: world_news_claude_short__Full_event_details-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 1259
    num_examples: 5
  download_size: 2637
  dataset_size: 1259
- config_name: world_news_claude_short__Other_entities-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 40430
    num_examples: 20
  download_size: 32620
  dataset_size: 40430
- config_name: world_news_claude_short__Other_entities-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 198
    num_examples: 5
  download_size: 1790
  dataset_size: 198
- config_name: world_news_claude_short__Other_entities-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 809
    num_examples: 5
  download_size: 2157
  dataset_size: 809
- config_name: world_news_claude_short__Spaces-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 40430
    num_examples: 20
  download_size: 32620
  dataset_size: 40430
- config_name: world_news_claude_short__Spaces-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 4003
    num_examples: 99
  download_size: 2293
  dataset_size: 4003
- config_name: world_news_claude_short__Spaces-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 10811
    num_examples: 68
  download_size: 3705
  dataset_size: 10811
- config_name: world_news_claude_short__Times-corpus
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  - name: title
    dtype: string
  splits:
  - name: test
    num_bytes: 40430
    num_examples: 20
  download_size: 32620
  dataset_size: 40430
- config_name: world_news_claude_short__Times-qrels
  features:
  - name: query-id
    dtype: string
  - name: corpus-id
    dtype: string
  - name: score
    dtype: int64
  splits:
  - name: test
    num_bytes: 4407
    num_examples: 109
  download_size: 2325
  dataset_size: 4407
- config_name: world_news_claude_short__Times-queries
  features:
  - name: id
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: test
    num_bytes: 11212
    num_examples: 73
  download_size: 3709
  dataset_size: 11212
configs:
- config_name: default_claude_long__Entities-corpus
  data_files:
  - split: test
    path: default_claude_long/Entities-corpus/test-*
- config_name: default_claude_long__Entities-qrels
  data_files:
  - split: test
    path: default_claude_long/Entities-qrels/test-*
- config_name: default_claude_long__Entities-queries
  data_files:
  - split: test
    path: default_claude_long/Entities-queries/test-*
- config_name: default_claude_long__Event_contents-corpus
  data_files:
  - split: test
    path: default_claude_long/Event_contents-corpus/test-*
- config_name: default_claude_long__Event_contents-qrels
  data_files:
  - split: test
    path: default_claude_long/Event_contents-qrels/test-*
- config_name: default_claude_long__Event_contents-queries
  data_files:
  - split: test
    path: default_claude_long/Event_contents-queries/test-*
- config_name: default_claude_long__Full_event_details-corpus
  data_files:
  - split: test
    path: default_claude_long/Full_event_details-corpus/test-*
- config_name: default_claude_long__Full_event_details-qrels
  data_files:
  - split: test
    path: default_claude_long/Full_event_details-qrels/test-*
- config_name: default_claude_long__Full_event_details-queries
  data_files:
  - split: test
    path: default_claude_long/Full_event_details-queries/test-*
- config_name: default_claude_long__Other_entities-corpus
  data_files:
  - split: test
    path: default_claude_long/Other_entities-corpus/test-*
- config_name: default_claude_long__Other_entities-qrels
  data_files:
  - split: test
    path: default_claude_long/Other_entities-qrels/test-*
- config_name: default_claude_long__Other_entities-queries
  data_files:
  - split: test
    path: default_claude_long/Other_entities-queries/test-*
- config_name: default_claude_long__Spaces-corpus
  data_files:
  - split: test
    path: default_claude_long/Spaces-corpus/test-*
- config_name: default_claude_long__Spaces-qrels
  data_files:
  - split: test
    path: default_claude_long/Spaces-qrels/test-*
- config_name: default_claude_long__Spaces-queries
  data_files:
  - split: test
    path: default_claude_long/Spaces-queries/test-*
- config_name: default_claude_long__Times-corpus
  data_files:
  - split: test
    path: default_claude_long/Times-corpus/test-*
- config_name: default_claude_long__Times-qrels
  data_files:
  - split: test
    path: default_claude_long/Times-qrels/test-*
- config_name: default_claude_long__Times-queries
  data_files:
  - split: test
    path: default_claude_long/Times-queries/test-*
- config_name: default_claude_short__Entities-corpus
  data_files:
  - split: test
    path: default_claude_short/Entities-corpus/test-*
- config_name: default_claude_short__Entities-qrels
  data_files:
  - split: test
    path: default_claude_short/Entities-qrels/test-*
- config_name: default_claude_short__Entities-queries
  data_files:
  - split: test
    path: default_claude_short/Entities-queries/test-*
- config_name: default_claude_short__Event_contents-corpus
  data_files:
  - split: test
    path: default_claude_short/Event_contents-corpus/test-*
- config_name: default_claude_short__Event_contents-qrels
  data_files:
  - split: test
    path: default_claude_short/Event_contents-qrels/test-*
- config_name: default_claude_short__Event_contents-queries
  data_files:
  - split: test
    path: default_claude_short/Event_contents-queries/test-*
- config_name: default_claude_short__Full_event_details-corpus
  data_files:
  - split: test
    path: default_claude_short/Full_event_details-corpus/test-*
- config_name: default_claude_short__Full_event_details-qrels
  data_files:
  - split: test
    path: default_claude_short/Full_event_details-qrels/test-*
- config_name: default_claude_short__Full_event_details-queries
  data_files:
  - split: test
    path: default_claude_short/Full_event_details-queries/test-*
- config_name: default_claude_short__Other_entities-corpus
  data_files:
  - split: test
    path: default_claude_short/Other_entities-corpus/test-*
- config_name: default_claude_short__Other_entities-qrels
  data_files:
  - split: test
    path: default_claude_short/Other_entities-qrels/test-*
- config_name: default_claude_short__Other_entities-queries
  data_files:
  - split: test
    path: default_claude_short/Other_entities-queries/test-*
- config_name: default_claude_short__Spaces-corpus
  data_files:
  - split: test
    path: default_claude_short/Spaces-corpus/test-*
- config_name: default_claude_short__Spaces-qrels
  data_files:
  - split: test
    path: default_claude_short/Spaces-qrels/test-*
- config_name: default_claude_short__Spaces-queries
  data_files:
  - split: test
    path: default_claude_short/Spaces-queries/test-*
- config_name: default_claude_short__Times-corpus
  data_files:
  - split: test
    path: default_claude_short/Times-corpus/test-*
- config_name: default_claude_short__Times-qrels
  data_files:
  - split: test
    path: default_claude_short/Times-qrels/test-*
- config_name: default_claude_short__Times-queries
  data_files:
  - split: test
    path: default_claude_short/Times-queries/test-*
- config_name: default_claude_very_long__Entities-corpus
  data_files:
  - split: test
    path: default_claude_very_long/Entities-corpus/test-*
- config_name: default_claude_very_long__Entities-qrels
  data_files:
  - split: test
    path: default_claude_very_long/Entities-qrels/test-*
- config_name: default_claude_very_long__Entities-queries
  data_files:
  - split: test
    path: default_claude_very_long/Entities-queries/test-*
- config_name: default_claude_very_long__Event_contents-corpus
  data_files:
  - split: test
    path: default_claude_very_long/Event_contents-corpus/test-*
- config_name: default_claude_very_long__Event_contents-qrels
  data_files:
  - split: test
    path: default_claude_very_long/Event_contents-qrels/test-*
- config_name: default_claude_very_long__Event_contents-queries
  data_files:
  - split: test
    path: default_claude_very_long/Event_contents-queries/test-*
- config_name: default_claude_very_long__Full_event_details-corpus
  data_files:
  - split: test
    path: default_claude_very_long/Full_event_details-corpus/test-*
- config_name: default_claude_very_long__Full_event_details-qrels
  data_files:
  - split: test
    path: default_claude_very_long/Full_event_details-qrels/test-*
- config_name: default_claude_very_long__Full_event_details-queries
  data_files:
  - split: test
    path: default_claude_very_long/Full_event_details-queries/test-*
- config_name: default_claude_very_long__Other_entities-corpus
  data_files:
  - split: test
    path: default_claude_very_long/Other_entities-corpus/test-*
- config_name: default_claude_very_long__Other_entities-qrels
  data_files:
  - split: test
    path: default_claude_very_long/Other_entities-qrels/test-*
- config_name: default_claude_very_long__Other_entities-queries
  data_files:
  - split: test
    path: default_claude_very_long/Other_entities-queries/test-*
- config_name: default_claude_very_long__Spaces-corpus
  data_files:
  - split: test
    path: default_claude_very_long/Spaces-corpus/test-*
- config_name: default_claude_very_long__Spaces-qrels
  data_files:
  - split: test
    path: default_claude_very_long/Spaces-qrels/test-*
- config_name: default_claude_very_long__Spaces-queries
  data_files:
  - split: test
    path: default_claude_very_long/Spaces-queries/test-*
- config_name: default_claude_very_long__Times-corpus
  data_files:
  - split: test
    path: default_claude_very_long/Times-corpus/test-*
- config_name: default_claude_very_long__Times-qrels
  data_files:
  - split: test
    path: default_claude_very_long/Times-qrels/test-*
- config_name: default_claude_very_long__Times-queries
  data_files:
  - split: test
    path: default_claude_very_long/Times-queries/test-*
- config_name: default_gpt4o_long__Entities-corpus
  data_files:
  - split: test
    path: default_gpt4o_long/Entities-corpus/test-*
- config_name: default_gpt4o_long__Entities-qrels
  data_files:
  - split: test
    path: default_gpt4o_long/Entities-qrels/test-*
- config_name: default_gpt4o_long__Entities-queries
  data_files:
  - split: test
    path: default_gpt4o_long/Entities-queries/test-*
- config_name: default_gpt4o_long__Event_contents-corpus
  data_files:
  - split: test
    path: default_gpt4o_long/Event_contents-corpus/test-*
- config_name: default_gpt4o_long__Event_contents-qrels
  data_files:
  - split: test
    path: default_gpt4o_long/Event_contents-qrels/test-*
- config_name: default_gpt4o_long__Event_contents-queries
  data_files:
  - split: test
    path: default_gpt4o_long/Event_contents-queries/test-*
- config_name: default_gpt4o_long__Full_event_details-corpus
  data_files:
  - split: test
    path: default_gpt4o_long/Full_event_details-corpus/test-*
- config_name: default_gpt4o_long__Full_event_details-qrels
  data_files:
  - split: test
    path: default_gpt4o_long/Full_event_details-qrels/test-*
- config_name: default_gpt4o_long__Full_event_details-queries
  data_files:
  - split: test
    path: default_gpt4o_long/Full_event_details-queries/test-*
- config_name: default_gpt4o_long__Other_entities-corpus
  data_files:
  - split: test
    path: default_gpt4o_long/Other_entities-corpus/test-*
- config_name: default_gpt4o_long__Other_entities-qrels
  data_files:
  - split: test
    path: default_gpt4o_long/Other_entities-qrels/test-*
- config_name: default_gpt4o_long__Other_entities-queries
  data_files:
  - split: test
    path: default_gpt4o_long/Other_entities-queries/test-*
- config_name: default_gpt4o_long__Spaces-corpus
  data_files:
  - split: test
    path: default_gpt4o_long/Spaces-corpus/test-*
- config_name: default_gpt4o_long__Spaces-qrels
  data_files:
  - split: test
    path: default_gpt4o_long/Spaces-qrels/test-*
- config_name: default_gpt4o_long__Spaces-queries
  data_files:
  - split: test
    path: default_gpt4o_long/Spaces-queries/test-*
- config_name: default_gpt4o_long__Times-corpus
  data_files:
  - split: test
    path: default_gpt4o_long/Times-corpus/test-*
- config_name: default_gpt4o_long__Times-qrels
  data_files:
  - split: test
    path: default_gpt4o_long/Times-qrels/test-*
- config_name: default_gpt4o_long__Times-queries
  data_files:
  - split: test
    path: default_gpt4o_long/Times-queries/test-*
- config_name: default_gpt4o_short__Entities-corpus
  data_files:
  - split: test
    path: default_gpt4o_short/Entities-corpus/test-*
- config_name: default_gpt4o_short__Entities-qrels
  data_files:
  - split: test
    path: default_gpt4o_short/Entities-qrels/test-*
- config_name: default_gpt4o_short__Entities-queries
  data_files:
  - split: test
    path: default_gpt4o_short/Entities-queries/test-*
- config_name: default_gpt4o_short__Event_contents-corpus
  data_files:
  - split: test
    path: default_gpt4o_short/Event_contents-corpus/test-*
- config_name: default_gpt4o_short__Event_contents-qrels
  data_files:
  - split: test
    path: default_gpt4o_short/Event_contents-qrels/test-*
- config_name: default_gpt4o_short__Event_contents-queries
  data_files:
  - split: test
    path: default_gpt4o_short/Event_contents-queries/test-*
- config_name: default_gpt4o_short__Full_event_details-corpus
  data_files:
  - split: test
    path: default_gpt4o_short/Full_event_details-corpus/test-*
- config_name: default_gpt4o_short__Full_event_details-qrels
  data_files:
  - split: test
    path: default_gpt4o_short/Full_event_details-qrels/test-*
- config_name: default_gpt4o_short__Full_event_details-queries
  data_files:
  - split: test
    path: default_gpt4o_short/Full_event_details-queries/test-*
- config_name: default_gpt4o_short__Other_entities-corpus
  data_files:
  - split: test
    path: default_gpt4o_short/Other_entities-corpus/test-*
- config_name: default_gpt4o_short__Other_entities-qrels
  data_files:
  - split: test
    path: default_gpt4o_short/Other_entities-qrels/test-*
- config_name: default_gpt4o_short__Other_entities-queries
  data_files:
  - split: test
    path: default_gpt4o_short/Other_entities-queries/test-*
- config_name: default_gpt4o_short__Spaces-corpus
  data_files:
  - split: test
    path: default_gpt4o_short/Spaces-corpus/test-*
- config_name: default_gpt4o_short__Spaces-qrels
  data_files:
  - split: test
    path: default_gpt4o_short/Spaces-qrels/test-*
- config_name: default_gpt4o_short__Spaces-queries
  data_files:
  - split: test
    path: default_gpt4o_short/Spaces-queries/test-*
- config_name: default_gpt4o_short__Times-corpus
  data_files:
  - split: test
    path: default_gpt4o_short/Times-corpus/test-*
- config_name: default_gpt4o_short__Times-qrels
  data_files:
  - split: test
    path: default_gpt4o_short/Times-qrels/test-*
- config_name: default_gpt4o_short__Times-queries
  data_files:
  - split: test
    path: default_gpt4o_short/Times-queries/test-*
- config_name: sci_fi_claude_long__Entities-corpus
  data_files:
  - split: test
    path: sci_fi_claude_long/Entities-corpus/test-*
- config_name: sci_fi_claude_long__Entities-qrels
  data_files:
  - split: test
    path: sci_fi_claude_long/Entities-qrels/test-*
- config_name: sci_fi_claude_long__Entities-queries
  data_files:
  - split: test
    path: sci_fi_claude_long/Entities-queries/test-*
- config_name: sci_fi_claude_long__Event_contents-corpus
  data_files:
  - split: test
    path: sci_fi_claude_long/Event_contents-corpus/test-*
- config_name: sci_fi_claude_long__Event_contents-qrels
  data_files:
  - split: test
    path: sci_fi_claude_long/Event_contents-qrels/test-*
- config_name: sci_fi_claude_long__Event_contents-queries
  data_files:
  - split: test
    path: sci_fi_claude_long/Event_contents-queries/test-*
- config_name: sci_fi_claude_long__Full_event_details-corpus
  data_files:
  - split: test
    path: sci_fi_claude_long/Full_event_details-corpus/test-*
- config_name: sci_fi_claude_long__Full_event_details-qrels
  data_files:
  - split: test
    path: sci_fi_claude_long/Full_event_details-qrels/test-*
- config_name: sci_fi_claude_long__Full_event_details-queries
  data_files:
  - split: test
    path: sci_fi_claude_long/Full_event_details-queries/test-*
- config_name: sci_fi_claude_long__Other_entities-corpus
  data_files:
  - split: test
    path: sci_fi_claude_long/Other_entities-corpus/test-*
- config_name: sci_fi_claude_long__Other_entities-qrels
  data_files:
  - split: test
    path: sci_fi_claude_long/Other_entities-qrels/test-*
- config_name: sci_fi_claude_long__Other_entities-queries
  data_files:
  - split: test
    path: sci_fi_claude_long/Other_entities-queries/test-*
- config_name: sci_fi_claude_long__Spaces-corpus
  data_files:
  - split: test
    path: sci_fi_claude_long/Spaces-corpus/test-*
- config_name: sci_fi_claude_long__Spaces-qrels
  data_files:
  - split: test
    path: sci_fi_claude_long/Spaces-qrels/test-*
- config_name: sci_fi_claude_long__Spaces-queries
  data_files:
  - split: test
    path: sci_fi_claude_long/Spaces-queries/test-*
- config_name: sci_fi_claude_long__Times-corpus
  data_files:
  - split: test
    path: sci_fi_claude_long/Times-corpus/test-*
- config_name: sci_fi_claude_long__Times-qrels
  data_files:
  - split: test
    path: sci_fi_claude_long/Times-qrels/test-*
- config_name: sci_fi_claude_long__Times-queries
  data_files:
  - split: test
    path: sci_fi_claude_long/Times-queries/test-*
- config_name: sci_fi_claude_short__Entities-corpus
  data_files:
  - split: test
    path: sci_fi_claude_short/Entities-corpus/test-*
- config_name: sci_fi_claude_short__Entities-qrels
  data_files:
  - split: test
    path: sci_fi_claude_short/Entities-qrels/test-*
- config_name: sci_fi_claude_short__Entities-queries
  data_files:
  - split: test
    path: sci_fi_claude_short/Entities-queries/test-*
- config_name: sci_fi_claude_short__Event_contents-corpus
  data_files:
  - split: test
    path: sci_fi_claude_short/Event_contents-corpus/test-*
- config_name: sci_fi_claude_short__Event_contents-qrels
  data_files:
  - split: test
    path: sci_fi_claude_short/Event_contents-qrels/test-*
- config_name: sci_fi_claude_short__Event_contents-queries
  data_files:
  - split: test
    path: sci_fi_claude_short/Event_contents-queries/test-*
- config_name: sci_fi_claude_short__Full_event_details-corpus
  data_files:
  - split: test
    path: sci_fi_claude_short/Full_event_details-corpus/test-*
- config_name: sci_fi_claude_short__Full_event_details-qrels
  data_files:
  - split: test
    path: sci_fi_claude_short/Full_event_details-qrels/test-*
- config_name: sci_fi_claude_short__Full_event_details-queries
  data_files:
  - split: test
    path: sci_fi_claude_short/Full_event_details-queries/test-*
- config_name: sci_fi_claude_short__Other_entities-corpus
  data_files:
  - split: test
    path: sci_fi_claude_short/Other_entities-corpus/test-*
- config_name: sci_fi_claude_short__Other_entities-qrels
  data_files:
  - split: test
    path: sci_fi_claude_short/Other_entities-qrels/test-*
- config_name: sci_fi_claude_short__Other_entities-queries
  data_files:
  - split: test
    path: sci_fi_claude_short/Other_entities-queries/test-*
- config_name: sci_fi_claude_short__Spaces-corpus
  data_files:
  - split: test
    path: sci_fi_claude_short/Spaces-corpus/test-*
- config_name: sci_fi_claude_short__Spaces-qrels
  data_files:
  - split: test
    path: sci_fi_claude_short/Spaces-qrels/test-*
- config_name: sci_fi_claude_short__Spaces-queries
  data_files:
  - split: test
    path: sci_fi_claude_short/Spaces-queries/test-*
- config_name: sci_fi_claude_short__Times-corpus
  data_files:
  - split: test
    path: sci_fi_claude_short/Times-corpus/test-*
- config_name: sci_fi_claude_short__Times-qrels
  data_files:
  - split: test
    path: sci_fi_claude_short/Times-qrels/test-*
- config_name: sci_fi_claude_short__Times-queries
  data_files:
  - split: test
    path: sci_fi_claude_short/Times-queries/test-*
- config_name: world_news_claude_long__Entities-corpus
  data_files:
  - split: test
    path: world_news_claude_long/Entities-corpus/test-*
- config_name: world_news_claude_long__Entities-qrels
  data_files:
  - split: test
    path: world_news_claude_long/Entities-qrels/test-*
- config_name: world_news_claude_long__Entities-queries
  data_files:
  - split: test
    path: world_news_claude_long/Entities-queries/test-*
- config_name: world_news_claude_long__Event_contents-corpus
  data_files:
  - split: test
    path: world_news_claude_long/Event_contents-corpus/test-*
- config_name: world_news_claude_long__Event_contents-qrels
  data_files:
  - split: test
    path: world_news_claude_long/Event_contents-qrels/test-*
- config_name: world_news_claude_long__Event_contents-queries
  data_files:
  - split: test
    path: world_news_claude_long/Event_contents-queries/test-*
- config_name: world_news_claude_long__Full_event_details-corpus
  data_files:
  - split: test
    path: world_news_claude_long/Full_event_details-corpus/test-*
- config_name: world_news_claude_long__Full_event_details-qrels
  data_files:
  - split: test
    path: world_news_claude_long/Full_event_details-qrels/test-*
- config_name: world_news_claude_long__Full_event_details-queries
  data_files:
  - split: test
    path: world_news_claude_long/Full_event_details-queries/test-*
- config_name: world_news_claude_long__Other_entities-corpus
  data_files:
  - split: test
    path: world_news_claude_long/Other_entities-corpus/test-*
- config_name: world_news_claude_long__Other_entities-qrels
  data_files:
  - split: test
    path: world_news_claude_long/Other_entities-qrels/test-*
- config_name: world_news_claude_long__Other_entities-queries
  data_files:
  - split: test
    path: world_news_claude_long/Other_entities-queries/test-*
- config_name: world_news_claude_long__Spaces-corpus
  data_files:
  - split: test
    path: world_news_claude_long/Spaces-corpus/test-*
- config_name: world_news_claude_long__Spaces-qrels
  data_files:
  - split: test
    path: world_news_claude_long/Spaces-qrels/test-*
- config_name: world_news_claude_long__Spaces-queries
  data_files:
  - split: test
    path: world_news_claude_long/Spaces-queries/test-*
- config_name: world_news_claude_long__Times-corpus
  data_files:
  - split: test
    path: world_news_claude_long/Times-corpus/test-*
- config_name: world_news_claude_long__Times-qrels
  data_files:
  - split: test
    path: world_news_claude_long/Times-qrels/test-*
- config_name: world_news_claude_long__Times-queries
  data_files:
  - split: test
    path: world_news_claude_long/Times-queries/test-*
- config_name: world_news_claude_short__Entities-corpus
  data_files:
  - split: test
    path: world_news_claude_short/Entities-corpus/test-*
- config_name: world_news_claude_short__Entities-qrels
  data_files:
  - split: test
    path: world_news_claude_short/Entities-qrels/test-*
- config_name: world_news_claude_short__Entities-queries
  data_files:
  - split: test
    path: world_news_claude_short/Entities-queries/test-*
- config_name: world_news_claude_short__Event_contents-corpus
  data_files:
  - split: test
    path: world_news_claude_short/Event_contents-corpus/test-*
- config_name: world_news_claude_short__Event_contents-qrels
  data_files:
  - split: test
    path: world_news_claude_short/Event_contents-qrels/test-*
- config_name: world_news_claude_short__Event_contents-queries
  data_files:
  - split: test
    path: world_news_claude_short/Event_contents-queries/test-*
- config_name: world_news_claude_short__Full_event_details-corpus
  data_files:
  - split: test
    path: world_news_claude_short/Full_event_details-corpus/test-*
- config_name: world_news_claude_short__Full_event_details-qrels
  data_files:
  - split: test
    path: world_news_claude_short/Full_event_details-qrels/test-*
- config_name: world_news_claude_short__Full_event_details-queries
  data_files:
  - split: test
    path: world_news_claude_short/Full_event_details-queries/test-*
- config_name: world_news_claude_short__Other_entities-corpus
  data_files:
  - split: test
    path: world_news_claude_short/Other_entities-corpus/test-*
- config_name: world_news_claude_short__Other_entities-qrels
  data_files:
  - split: test
    path: world_news_claude_short/Other_entities-qrels/test-*
- config_name: world_news_claude_short__Other_entities-queries
  data_files:
  - split: test
    path: world_news_claude_short/Other_entities-queries/test-*
- config_name: world_news_claude_short__Spaces-corpus
  data_files:
  - split: test
    path: world_news_claude_short/Spaces-corpus/test-*
- config_name: world_news_claude_short__Spaces-qrels
  data_files:
  - split: test
    path: world_news_claude_short/Spaces-qrels/test-*
- config_name: world_news_claude_short__Spaces-queries
  data_files:
  - split: test
    path: world_news_claude_short/Spaces-queries/test-*
- config_name: world_news_claude_short__Times-corpus
  data_files:
  - split: test
    path: world_news_claude_short/Times-corpus/test-*
- config_name: world_news_claude_short__Times-qrels
  data_files:
  - split: test
    path: world_news_claude_short/Times-qrels/test-*
- config_name: world_news_claude_short__Times-queries
  data_files:
  - split: test
    path: world_news_claude_short/Times-queries/test-*
tags:
- mteb
- text
---
<!-- adapted from https://github.com/huggingface/huggingface_hub/blob/v0.30.2/src/huggingface_hub/templates/datasetcard_template.md -->

## Local Project Provenance

- Project role: primary episodic-memory retrieval dataset.
- Download date: 2026-07-18.
- Hugging Face source: https://huggingface.co/datasets/mteb/EPBench
- LMEB GitHub: https://github.com/KaLM-Embedding/LMEB
- LMEB Hugging Face: https://huggingface.co/datasets/KaLM-Embedding/LMEB
- Upstream EPBench GitHub: https://github.com/ahstat/episodic-memory-benchmark
- Local copy scope: full `mteb/EPBench` dataset repository, copied without `.git`.

### Local Citation Set

```bibtex
@misc{zhao2026lmeb,
  title = {LMEB: Long-horizon Memory Embedding Benchmark},
  author = {Xinping Zhao and Xinshuo Hu and Jiaxin Xu and Danyu Tang and Xin Zhang and Mengjia Zhou and Yan Zhong and Yao Zhou and Zifei Shan and Meishan Zhang and Baotian Hu and Min Zhang},
  year = {2026},
  eprint = {2603.12572},
  archivePrefix = {arXiv},
  primaryClass = {cs.CL},
  url = {https://arxiv.org/abs/2603.12572}
}

@article{2025epmembench,
  title = {Episodic Memories Generation and Evaluation Benchmark for Large Language Models},
  author = {Huet, Alexis and Ben Houidi, Zied and Rossi, Dario},
  journal = {International Conference on Learning Representations},
  year = {2025}
}
```

<div align="center" style="padding: 40px 20px; background-color: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); max-width: 600px; margin: 0 auto;">
  <h1 style="font-size: 3.5rem; color: #1a1a1a; margin: 0 0 20px 0; letter-spacing: 2px; font-weight: 700;">EPBench</h1>
  <div style="font-size: 1.5rem; color: #4a4a4a; margin-bottom: 5px; font-weight: 300;">An <a href="https://github.com/embeddings-benchmark/mteb" style="color: #2c5282; font-weight: 600; text-decoration: none;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">MTEB</a> dataset</div>
  <div style="font-size: 0.9rem; color: #2c5282; margin-top: 10px;">Massive Text Embedding Benchmark</div>
</div>

LMEB episodic-memory retrieval task based on EPBench, evaluating event-centric retrieval across generator, context-length, and query-type variants.

|               |                                             |
|---------------|---------------------------------------------|
| Task category | Retrieval (text-to-text)                              |
| Domains       | Fiction, News, Written                               |
| Reference     | [LMEB: Long-horizon Memory Embedding Benchmark](https://doi.org/10.6084/m9.figshare.28244480) |

Source datasets:
- [KaLM-Embedding/LMEB](https://huggingface.co/datasets/KaLM-Embedding/LMEB)


## How to evaluate on this task

You can evaluate an embedding model on this dataset using the following code:

```python
import mteb

task = mteb.get_task("EPBench")
model = mteb.get_model(YOUR_MODEL)
mteb.evaluate(model, task)
```

<!-- Datasets want link to arxiv in readme to autolink dataset with paper -->
To learn more about how to run models on `mteb` task check out the [GitHub repository](https://github.com/embeddings-benchmark/mteb).

## Citation

If you use this dataset, please cite the dataset as well as [mteb](https://github.com/embeddings-benchmark/mteb), as this dataset likely includes additional processing as a part of the [MMTEB Contribution](https://github.com/embeddings-benchmark/mteb/tree/main/docs/mmteb).

```bibtex

@misc{zhao2026lmeb,
  archiveprefix = {arXiv},
  author = {Zhao, Xinping and Hu, Xinshuo and Xu, Jiaxin and Tang, Danyu and Zhang, Xin and Zhou, Mengjia and Zhong, Yan and Zhou, Yao and Shan, Zifei and Zhang, Meishan and Hu, Baotian and Zhang, Min},
  eprint = {2603.12572},
  primaryclass = {cs.CL},
  title = {LMEB: Long-horizon Memory Embedding Benchmark},
  url = {https://arxiv.org/abs/2603.12572},
  year = {2026},
}


@article{enevoldsen2025mmtebmassivemultilingualtext,
  title={MMTEB: Massive Multilingual Text Embedding Benchmark},
  author={Kenneth Enevoldsen and Isaac Chung and Imene Kerboua and Márton Kardos and Ashwin Mathur and David Stap and Jay Gala and Wissam Siblini and Dominik Krzemiński and Genta Indra Winata and Saba Sturua and Saiteja Utpala and Mathieu Ciancone and Marion Schaeffer and Gabriel Sequeira and Diganta Misra and Shreeya Dhakal and Jonathan Rystrøm and Roman Solomatin and Ömer Çağatan and Akash Kundu and Martin Bernstorff and Shitao Xiao and Akshita Sukhlecha and Bhavish Pahwa and Rafał Poświata and Kranthi Kiran GV and Shawon Ashraf and Daniel Auras and Björn Plüster and Jan Philipp Harries and Loïc Magne and Isabelle Mohr and Mariya Hendriksen and Dawei Zhu and Hippolyte Gisserot-Boukhlef and Tom Aarsen and Jan Kostkan and Konrad Wojtasik and Taemin Lee and Marek Šuppa and Crystina Zhang and Roberta Rocca and Mohammed Hamdy and Andrianos Michail and John Yang and Manuel Faysse and Aleksei Vatolin and Nandan Thakur and Manan Dey and Dipam Vasani and Pranjal Chitale and Simone Tedeschi and Nguyen Tai and Artem Snegirev and Michael Günther and Mengzhou Xia and Weijia Shi and Xing Han Lù and Jordan Clive and Gayatri Krishnakumar and Anna Maksimova and Silvan Wehrli and Maria Tikhonova and Henil Panchal and Aleksandr Abramov and Malte Ostendorff and Zheng Liu and Simon Clematide and Lester James Miranda and Alena Fenogenova and Guangyu Song and Ruqiya Bin Safi and Wen-Ding Li and Alessia Borghini and Federico Cassano and Hongjin Su and Jimmy Lin and Howard Yen and Lasse Hansen and Sara Hooker and Chenghao Xiao and Vaibhav Adlakha and Orion Weller and Siva Reddy and Niklas Muennighoff},
  publisher = {arXiv},
  journal={arXiv preprint arXiv:2502.13595},
  year={2025},
  url={https://arxiv.org/abs/2502.13595},
  doi = {10.48550/arXiv.2502.13595},
}

@article{muennighoff2022mteb,
  author = {Muennighoff, Niklas and Tazi, Nouamane and Magne, Loïc and Reimers, Nils},
  title = {MTEB: Massive Text Embedding Benchmark},
  publisher = {arXiv},
  journal={arXiv preprint arXiv:2210.07316},
  year = {2022}
  url = {https://arxiv.org/abs/2210.07316},
  doi = {10.48550/ARXIV.2210.07316},
}
```

# Dataset Statistics
<details>
  <summary> Dataset Statistics</summary>

The following code contains the descriptive statistics from the task. These can also be obtained using:

```python
import mteb

task = mteb.get_task("EPBench")

desc_stats = task.metadata.descriptive_stats
```

```json
{
    "test": {
        "num_samples": 20672,
        "number_of_characters": 43680541,
        "documents_text_statistics": {
            "total_text_length": 43129824,
            "min_text_length": 653,
            "average_text_length": 2532.876673713883,
            "max_text_length": 5542,
            "unique_texts": 2563
        },
        "documents_image_statistics": null,
        "documents_audio_statistics": null,
        "queries_text_statistics": {
            "total_text_length": 550717,
            "min_text_length": 82,
            "average_text_length": 151.12980241492866,
            "max_text_length": 263,
            "unique_texts": 2026
        },
        "queries_image_statistics": null,
        "queries_audio_statistics": null,
        "relevant_docs_statistics": {
            "num_relevant_docs": 11458,
            "min_relevant_docs_per_query": 1,
            "average_relevant_docs_per_query": 3.1443468715697036,
            "max_relevant_docs_per_query": 138,
            "unique_relevant_docs": 5418
        },
        "top_ranked_statistics": null
    }
}
```

</details>

---
*This dataset card was automatically generated using [MTEB](https://github.com/embeddings-benchmark/mteb)*
