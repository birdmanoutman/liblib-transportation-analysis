### Field Dictionary · Liblib Transportation

Maps Liblib API fields to DB schema (see `docs/PRD_transportation_scraper.md`). This draft will be refined after sample capture.

#### List: img/group/search → works

| API field (likely) | Type | DB column | Notes |
|---|---|---|---|
| slug | string | `works.slug` | Unique per work |
| title | string | `works.title` | |
| publishTime / createdAt | datetime | `works.published_at` | parse to UTC |
| tags | array | `works.tags_json` | store as JSON |
| likeCount | int | `works.like_count` | |
| favoriteCount | int | `works.favorite_count` | |
| commentCount | int | `works.comment_count` | |
| author.nickName | string | join via `authors.name` | resolved in detail/author API |
| author.id | string | `authors.external_author_id` | via detail/author API |

#### Detail: img/group/get/{slug} → works, work_models, work_images

| API field (likely) | Type | DB column | Notes |
|---|---|---|---|
| slug | string | `works.slug` | |
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

#### Author: img/author/{slug} → authors

| API field (likely) | Type | DB column | Notes |
|---|---|---|---|
| id | string | `authors.external_author_id` | |
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


