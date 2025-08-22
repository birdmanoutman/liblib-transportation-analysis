### Field Dictionary · Liblib Transportation

Maps Liblib API fields to DB schema (see `docs/PRD_transportation_scraper.md`). This draft will be refined after sample capture.

#### List: img/group/search → works

- Items come under `data.data` (array). Use `uuid` as the work identifier.

| API field | Type | DB column | Notes |
|---|---|---|---|
| uuid | string | `works.uuid` | Primary external ID |
| title | string | `works.title` | may be empty |
| createTime | datetime | `works.created_at` | to UTC |
| auditTime / updateTime | datetime | `works.updated_at` | to UTC |
| width | int | `works.width` | |
| height | int | `works.height` | |
| likeCount | int | `works.like_count` | |
| commentCount | int | `works.comment_count` | |
| tagsId | array<int> | `works.tags_id_json` | store as JSON |
| tagsLabel | string | `works.tags_label` | |
| userUuid | string | `authors.external_author_id` | join key to authors |
| nickname | string | `authors.name` | denormalize or via authors table |
| avatar | string | `authors.avatar_url` | denormalize or via authors table |
| imageUrl | string | `work_images.src_url` | first image |
| imageSource | int | `works.image_source` | raw enum/int |

#### Detail: img/group/get/{uuid} → works, work_models, work_images

| API field | Type | DB column | Notes |
|---|---|---|---|
| uuid | string | `works.uuid` | |
| title | string | `works.title` | |
| prompt | string | `works.prompt` | |
| negativePrompt | string | `works.negative_prompt` | |
| sampler | string | `works.sampler` | |
| steps | int | `works.steps` | |
| cfgScale | number | `works.cfg_scale` | |
| width | int | `works.width` | |
| height | int | `works.height` | |
| seed | string | `works.seed` | keep as text |
| images[].url | string | `work_images.src_url` | one row per image |
| images[].width | int | `work_images.width` | |
| images[].height | int | `work_images.height` | |
| images[].format | string | `work_images.format` | infer if missing |
| models[].name | string | `work_models.model_name` | for referenced models |
| models[].type | enum | `work_models.model_type` | map to CHECKPOINT/LORA/OTHER |

#### Author: img/author/{userUuid} → authors

| API field | Type | DB column | Notes |
|---|---|---|---|
| id (userUuid) | string | `authors.external_author_id` | |
| nickName | string | `authors.name` | |
| avatar | string | `authors.avatar_url` | |
| profileUrl | string | `authors.profile_url` | |

#### Comments (optional): community/commentList → comments

| API field (likely) | Type | DB column | Notes |
|---|---|---|---|
| content | string | `comments.content` | |
| createdAt | datetime | `comments.commented_at` | |
| user.nickName | string | `comments.commenter_name` | |
| user.avatar | string | `comments.commenter_avatar_url` | |

#### Conventions

- Datetime: parse to UTC, store as DATETIME.
- JSON: store raw arrays/objects where appropriate, with validation via pydantic later.
- Missing fields: default to NULL in DB; handle in ETL.


