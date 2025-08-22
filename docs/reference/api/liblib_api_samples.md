### Liblib API Samples (Transportation)

- **Goal**: Archive 3 list pages and 10 details JSON for the Transportation (汽车交通) category to support downstream schema design and parser contracts.
- **Outputs**:
  - `data/raw/liblib/samples/lists/list_page_{1..3}.json`
  - `data/raw/liblib/samples/details/detail_{uuid}.json`
  - `data/raw/liblib/samples/details/author_{userUuid|uuid}.json`

### How to run

```bash
python src/scraping/liblib_api_sampler.py \
  --pages 3 \
  --max-details 10 \
  --out-dir data/raw/liblib/samples
```

### Optional: supply captured payload for img/group/search

If you have a captured request body from your browser/devtools, save it to a JSON file and pass it via `--payload-file`:

```bash
python src/scraping/liblib_api_sampler.py \
  --payload-file payloads/list_payload.json \
  --pages 3 \
  --max-details 10
```

Example payload structure (captured from production – 汽车交通 tag):

```json
{"cid":"<cid>",
 "requestId":"<uuid>",
 "page":1,
 "pageSize":30,
 "sort":0,
 "followed":0,
 "resolution":0,
 "tagId":1773,
 "types":[],
 "createTools":[],
 "imageFuncs":[],
 "liked":0,
 "imageSources":[],
 "imageCapability":[]}
```

### Notes

- The sampler is conservative on concurrency and uses small delays to respect rate limits.
- If the site schema changes, provide a real captured payload to improve reliability.
- Samples are raw responses without transformation to help build field dictionaries and validators.


