# Performance testing report

## Test data

See [seed_perf_testing.py](./src/seed_perf_testing.py)

- 1 million users
- 1 million recipes
- 1 million (minus one) reviews for a single recipe

## Baseline performance (without database indices or improved queries)

The response times of the requests were gathered manually using browser
developer tools (Google Chrome). Three samples were taken of each query
before and after the improvements. Only GET methods were tested.

| Method | URL                                              | Sample 1  | Sample 2 | Sample 3 |
|--------|--------------------------------------------------|-----------|----------|----------|
| GET    | http://localhost:5000/                           | 12.77 s   | 12.62 s | 12.91 s   |
| GET    | http://localhost:5000/recipes                    | 9.18 s    | 8.89 s  | 8.90 s    |
| GET    | http://localhost:5000/recipes?page=2             | 15.38 s   | 14.36 s | 14.15 s   |
| GET    | http://localhost:5000/recipes?page=50000         | (timeout) | N/A     | N/A       |
| GET    | http://localhost:5000/recipes?query=Lorem        | 8.22 s    | 8.23 s  | 8.14 s    |
| GET    | http://localhost:5000/recipes?query=Lorem&page=2 | 14.12 s   | 13.97 s | 13.96 s   |
| GET    | http://localhost:5000/recipes/1                  | 175 ms    | 168 ms  | 154 ms    |
| GET    | http://localhost:5000/recipes/1?page=1           | 413 ms    | 463 ms  | 502 ms    |
| GET    | http://localhost:5000/recipes/1?page=100000      | 543 ms    | 560 ms  | 626 ms    |

The response times of the index and the recipe search pages are very poor,
especially if the page number is greater than one. The queries seem to perform
full table scans due to missing indices.

The response time of the recipe details page is acceptable. It is a bit curious
why the response time is higher when the page query parameter is explictly set
to one.

## Improved performance

The SQL query plans were investigated manually using the [EXPLAIN QUERY
PLAN](https://sqlite.org/eqp.html) command.

The following indices were added to the database:

```sql
CREATE INDEX idx_recipe__created_at ON recipe (datetime(created_at));
CREATE INDEX idx_recipe__title ON recipe (title);
CREATE INDEX idx_review__created_at ON review (datetime(created_at));
CREATE INDEX idx_review__recipe_id ON review (recipe_id);
CREATE INDEX idx_review__recipe_id_user_id ON review (recipe_id, user_id);
```

The recipe queries were also updated to perform a subquery for the tags
instead of outer joins with grouping:

```sql
SELECT
    ...
    (
        SELECT group_concat(tag.name, ', ')
        FROM tag
        INNER JOIN recipe_tag ON tag.id = recipe_tag.tag_id
        WHERE recipe_tag.recipe_id = recipe.id
    ) tags,
    ...
FROM recipe
```

The response times are now mostly under one second. The only exception is the
recipe search query which can take multiple seconds to execute when the page
number is large. The query plan is probably still not very optimal with the two
aggregate subqueries. The offset pagination is another factor (cursor-based
pagination could be more performant).

Curiously, the response times of the recipe details page queries seemed to
increase slightly after these changes. Perhaps the initial measurements were
somehow faulty?

| Method | URL                                              | Sample 1 | Sample 2 | Sample 3 |
|--------|--------------------------------------------------|----------|----------|----------|
| GET    | http://localhost:5000/                           | 322 ms   | 315 ms   | 320 ms   |
| GET    | http://localhost:5000/recipes                    | 607 ms   | 562 ms   | 554 ms   |
| GET    | http://localhost:5000/recipes?page=2             | 344 ms   | 352 ms   | 343 ms   |
| GET    | http://localhost:5000/recipes?page=50000         | 1.89 s   | 1.92 s   | 1.97 s   |
| GET    | http://localhost:5000/recipes?query=Lorem        | 676 ms   | 703 ms   | 670 ms   |
| GET    | http://localhost:5000/recipes?query=Lorem&page=2 | 669 ms   | 661 ms   | 743 ms   |
| GET    | http://localhost:5000/recipes/1                  | 609 ms   | 588 ms   | 596 ms   |
| GET    | http://localhost:5000/recipes/1?page=1           | 591 ms   | 598 ms   | 608 ms   |
| GET    | http://localhost:5000/recipes/1?page=100000      | 703 ms   | 736 ms   | 729 ms   |
