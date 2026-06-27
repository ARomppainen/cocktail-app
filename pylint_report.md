# Pylint report

The report is generated using the following command

```sh
poetry run pylint src/*.py
```

Here is the output

```sh
************* Module app
src/app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/app.py:31:0: C0115: Missing class docstring (missing-class-docstring)
src/app.py:34:4: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:39:4: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:43:4: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:47:4: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:51:4: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:59:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:66:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:73:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:78:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:85:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:90:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:120:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:129:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:134:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:168:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:198:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:210:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:238:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:263:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:292:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:324:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:336:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:360:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:396:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:425:0: C0116: Missing function or method docstring (missing-function-docstring)
src/app.py:459:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module db
src/db.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/db.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
src/db.py:11:0: C0116: Missing function or method docstring (missing-function-docstring)
src/db.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module forms
src/forms.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/forms.py:18:0: C0115: Missing class docstring (missing-class-docstring)
src/forms.py:23:4: C0116: Missing function or method docstring (missing-function-docstring)
src/forms.py:27:4: C0116: Missing function or method docstring (missing-function-docstring)
src/forms.py:47:0: C0115: Missing class docstring (missing-class-docstring)
src/forms.py:53:4: C0116: Missing function or method docstring (missing-function-docstring)
src/forms.py:57:4: C0116: Missing function or method docstring (missing-function-docstring)
src/forms.py:90:0: C0115: Missing class docstring (missing-class-docstring)
src/forms.py:97:4: C0116: Missing function or method docstring (missing-function-docstring)
src/forms.py:101:4: C0116: Missing function or method docstring (missing-function-docstring)
src/forms.py:141:0: C0115: Missing class docstring (missing-class-docstring)
src/forms.py:146:4: C0116: Missing function or method docstring (missing-function-docstring)
src/forms.py:161:0: C0115: Missing class docstring (missing-class-docstring)
src/forms.py:167:4: C0116: Missing function or method docstring (missing-function-docstring)
src/forms.py:171:4: C0116: Missing function or method docstring (missing-function-docstring)
************* Module recipes
src/recipes.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/recipes.py:8:0: C0116: Missing function or method docstring (missing-function-docstring)
src/recipes.py:38:0: C0116: Missing function or method docstring (missing-function-docstring)
src/recipes.py:82:0: C0116: Missing function or method docstring (missing-function-docstring)
src/recipes.py:112:0: C0116: Missing function or method docstring (missing-function-docstring)
src/recipes.py:172:0: C0116: Missing function or method docstring (missing-function-docstring)
src/recipes.py:201:0: C0116: Missing function or method docstring (missing-function-docstring)
src/recipes.py:245:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module reviews
src/reviews.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/reviews.py:8:0: C0116: Missing function or method docstring (missing-function-docstring)
src/reviews.py:56:0: C0116: Missing function or method docstring (missing-function-docstring)
src/reviews.py:90:0: C0116: Missing function or method docstring (missing-function-docstring)
src/reviews.py:109:0: C0116: Missing function or method docstring (missing-function-docstring)
src/reviews.py:129:0: C0116: Missing function or method docstring (missing-function-docstring)
src/reviews.py:147:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module seed
src/seed.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/seed.py:17:0: C0115: Missing class docstring (missing-class-docstring)
src/seed.py:23:0: C0115: Missing class docstring (missing-class-docstring)
src/seed.py:102:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module seed_perf_testing
src/seed_perf_testing.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/seed_perf_testing.py:52:0: C0115: Missing class docstring (missing-class-docstring)
src/seed_perf_testing.py:148:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module tags
src/tags.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/tags.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
src/tags.py:13:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module users
src/users.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/users.py:6:0: C0115: Missing class docstring (missing-class-docstring)
src/users.py:10:0: C0116: Missing function or method docstring (missing-function-docstring)
src/users.py:20:0: C0116: Missing function or method docstring (missing-function-docstring)
src/users.py:30:0: C0116: Missing function or method docstring (missing-function-docstring)
src/users.py:1:0: R0801: Similar lines in 2 files
==reviews:[130:148]
==seed_perf_testing:[131:140]
            INSERT INTO review (
                user_id,
                recipe_id,
                created_at,
                title,
                content,
                rating
            )
            VALUES (?, ?, datetime('now'), ?, ?, ?) (duplicate-code)

------------------------------------------------------------------
Your code has been rated at 8.77/10 (previous run: 8.77/10, +0.00)
```

## Docstring

Most of the findigs are related to Python
[docstrings](https://peps.python.org/pep-0257/), for example:

```sh
src/app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
src/app.py:31:0: C0115: Missing class docstring (missing-class-docstring)
src/app.py:34:4: C0116: Missing function or method docstring (missing-function-docstring)
```

Because I am the solo developer, I have decided to not use docstrings in this
project to save some time.


## Duplicate code

There is one finding related to duplicated code:

```sh
src/users.py:1:0: R0801: Similar lines in 2 files
==reviews:[130:148]
==seed_perf_testing:[131:140]
            INSERT INTO review (
                user_id,
                recipe_id,
                created_at,
                title,
                content,
                rating
            )
            VALUES (?, ?, datetime('now'), ?, ?, ?) (duplicate-code)
```

The `seed_perf_testing.py` script is used to generate a large amout of data
(millions of rows) for performance testing. Reusing the SQL functionality from
the main program would have been inefficient, because each call would have
created a new database connection instance (transaction per inserted row).
Hence, this query, and many other `INSERT` queries that Pylint does not detect,
are duplicated. The duplication could have been avoided by refactoring the main
program, but I did not deem that to be worthwhile.
